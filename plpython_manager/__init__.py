"""
Some Python functions are shared between the server and database.
To avoid repeating code (and accidentally ending up with different implementations),
shared functions are added to the PlPython3u Global Dictionary.
The functions are then callable from PlPython3u by using `GD["func_name"](arguments)`
"""
import inspect
from functools import partial
import textwrap
from typing import Sequence, Any, List, Callable

from sqlalchemy import text
from sqlalchemy import sql
from sqlalchemy.orm import Session


class _PlPythonManagerException(BaseException):
    """ Base exception for catchable errors thrown by PlPython Manger """

    # Private until we there is actually an expression to add


class PlPythonManager:
    def __init__(self) -> None:
        self.registered_objects: List[Any] = []

    def register(self, obj: Any) -> None:
        """ Registers an object to have its source copied to the PlPython Global Dictionary """
        self.registered_objects.append(obj)

    def copy_registered_objects_to_GD(self, db: Session) -> None:
        source = _prep_source(self.registered_objects)
        sql = _write_sql(source)
        _upload_to_postgres(db, sql)


def _prep_source(objs: Sequence[Callable]) -> str:
    # Keep in mind: "Reflection is never clever." https://go-proverbs.github.io/
    #  Unfortunately, reflection (introspection) seems like the best way
    #  to ensure the code on the server and in the database remain identical.
    source: List[str] = []
    for obj in objs:
        source.append(textwrap.dedent(inspect.getsource(obj)))
        source.append(f'\nGD["{obj.__name__}"] = {obj.__name__}\n\n')
    return "\n".join(source)[:-1]  # The final extraneous line is trimmed


def _write_sql(py_script: str) -> text:
    return text(
        f"""\
CREATE OR REPLACE FUNCTION add_to_gd()
RETURNS TEXT AS $$
{py_script}
$$ LANGUAGE plpython3u;
"""
    )


def _upload_to_postgres(db: Session, sql: sql.base.Executable) -> None:
    # Functions make unit testing more straightforward
    db.execute(sql)
    db.execute("SELECT add_to_gd()")


_default_manager = PlPythonManager()
register = partial(PlPythonManager.register, self=_default_manager)
