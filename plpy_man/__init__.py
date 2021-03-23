"""
Some Python functions are shared between the server and database.
To avoid repeating code (and accidentally ending up with different implementations),
shared functions are added to the PlPython3u Global Dictionary.
The functions are then callable from PlPython3u by using `GD["func_name"](arguments)`
"""
import enum
import inspect
import textwrap
from functools import partial
from typing import Sequence, Any, List, Callable, overload, Dict, TypedDict

from sqlalchemy import text
from sqlalchemy import sql
from sqlalchemy.orm import Session


class PlpyMan:
    def __init__(self) -> None:
        self._gd: List[Any] = []
        self.funcs: List[Callable] = []

    def to_gd(self, obj: Any) -> None:
        """ Registers an object to have its source copied to the PlPython Global Dictionary """
        self._gd.append(obj)

    def plpy_func(self, f):
        """ Decorator that registers a PlPython Func"""

    def flush(self, db: Session) -> None:
        source = _prep_source(self._gd)
        sql = _write_sql(source)
        _upload_to_postgres(db, sql)
        self._gd = []


_default_manager = PlpyMan()
to_gd = partial(PlpyMan.to_gd, self=_default_manager)
flush = partial(PlpyMan.flush, self=_default_manager)
plpy_func = partial(PlpyMan.plpy_func, self=_default_manager)


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
CREATE OR REPLACE FUNCTION _add_to_gd()
RETURNS TEXT AS $$
{py_script}
$$ LANGUAGE plpython3u;
"""
    )


def _upload_to_postgres(db: Session, sql: sql.base.Executable) -> None:
    # Functions make unit testing more straightforward
    db.execute(sql)
    db.execute("SELECT add_to_gd()")


##############################################################################
# Mocks
# https://www.postgresql.org/docs/13/plpython-sharing.html
SD: Dict = ...
GD: Dict = ...


# https://www.postgresql.org/docs/13/plpython-trigger.html
class TD(TypedDict):
    event: str
    when: str
    level: str
    new: Dict
    old: Dict
    name: str
    table_schema: str
    relid: str
    args: str


class plpy:
    """ Mocked plpy class that is automatically imported by methods on Plpy"""

    # https://www.postgresql.org/docs/13/plpython-database.html
    @overload
    def execute(self, query, max_rows=None):
        pass

    def prepare(self, query, argtypes=None):
        pass

    def execute(self, plan, arguments=None, max_rows=None):
        pass

    @overload
    def cursor(self, query):
        pass

    def cursor(self, plan, arguments=None):
        pass

    class SPIError(BaseException):
        pass

    class spiexceptions:
        # Todo: There is a lot to unpack here
        # https://www.postgresql.org/docs/13/errcodes-appendix.html#ERRCODES-TABLE
        pass

    # https://www.postgresql.org/docs/13/plpython-database.html
    def commit(self):
        pass

    def rollback(self):
        pass

    # https://www.postgresql.org/docs/13/plpython-util.html
    def debug(self, msg, **kwargs):
        pass

    def log(self, msg, **kwargs):
        pass

    def info(self, msg, **kwargs):
        pass

    def notice(self, msg, **kwargs):
        pass

    def warning(self, msg, **kwargs):
        pass

    def error(self, msg, **kwargs):
        pass

    def fatal(self, msg, **kwargs):
        pass

    def quote_ident(self, string):
        pass

    def quote_nullable(self, string):
        pass

    def quote_literal(self, string):
        pass


class Result:
    """ Mocked Result returned by plpy.execute """

    def nrows(self):
        pass

    def status(self):
        pass

    def colnames(self):
        pass

    def coltypes(self):
        pass

    def coltypmods(self):
        pass


class PlPyEnv(enum.Enum):
    # https://www.postgresql.org/docs/10/plpython-envar.html
    PYTHONHOME = "PYTHONHOME"
    PYTHONPATH = "PYTHONPATH"
    PYTHONY2K = "PYTHONY2K"
    PYTHONOPTIMIZE = "PYTHONOPTIMIZE"
    PYTHONDEBUG = "PYTHONDEBUG"
    PYTHONVERBOSE = "PYTHONVERBOSE"
    PYTHONCASEOK = "PYTHONCASEOK"
    PYTHONWRITEBYTECODE = "PYTHONWRITEBYTECODE"
    PYTHONIOENCODING = "PYTHONIOENCODING"
    PYTHONUSERBASE = "PYTHONUSERBASE"
    PYTHONHASHSEED = "PYTHONHASHSEED"


__cake__ = u'\u2728 \U0001f9b8\u200d\u2642\ufe0f \u2728'
