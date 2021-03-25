__all__ = ["SD", "GD", "TD", "plpy", "PLyPlan", "PLyResult", "PLyEnviron"]
import enum
from typing import Dict, TypedDict, Sequence, Any, Literal, ContextManager, Union
from unittest.mock import MagicMock

# https://www.postgresql.org/docs/13/plpython-sharing.html
SD: Dict = MagicMock()
GD: Dict = MagicMock()


# https://www.postgresql.org/docs/13/plpython-trigger.html
class _TriggerDict(TypedDict):
    event: Literal["INSERT", "UPDATE", "DELETE", "TRUNCATE"]
    when: Literal["BEFORE", "AFTER", "INSTEAD OF"]
    level: Literal["ROW", "STATEMENT"]
    new: Dict
    old: Dict
    name: str
    table_schema: Any
    relid: str
    args: Any


TD: _TriggerDict = MagicMock()


class PLyResult:
    """ Mocked Result returned by plpy.execute """

    def nrows(self, *args: Any) -> int:
        pass

    def status(self, *args: Any) -> int:
        pass

    def colnames(self) -> Sequence[str]:
        pass

    def coltypes(self) -> Sequence[str]:
        pass

    def coltypmods(self) -> Sequence[Sequence]:
        pass

    def __str__(self) -> str:
        ...


class PLyCursor:
    def fetch(self, *args: Any) -> PLyResult:
        ...

    def close(self) -> None:
        ...

    def __iter__(self) -> "PLyCursor":
        ...

    def __next__(self) -> PLyResult:
        ...


class PLyPlan:
    def cursor(self, *args: Any) -> PLyCursor:
        ...

    def execute(self, *args: Any) -> PLyResult:
        ...

    def status(self, *args: Any) -> int:
        ...


# https://www.postgresql.org/docs/13/plpython-database.html
class plpy:
    """ Mocked plpy class that is automatically imported by methods on Plpy"""

    def execute(self, query: Union[PLyPlan, str], *args: Any) -> PLyResult:
        ...

    def prepare(self, query: str, *args: Any) -> PLyPlan:
        ...

    def cursor(self, query: Union[PLyPlan, str], *args: Any) -> PLyCursor:
        ...

    class SPIError(BaseException):
        ...

    class spiexceptions:
        # Todo: There is a lot to unpack here
        # https://www.postgresql.org/docs/13/errcodes-appendix.html#ERRCODES-TABLE
        ...

    # https://www.postgresql.org/docs/13/plpython-database.html
    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def subtransaction(self) -> ContextManager:
        ...

    _log_kwargs = [
        "detail",
        "hint",
        "sqlstate",
        "schema_name",
        "column_name",
        "datatype_name",
        "constraint_name",
    ]

    # https://www.postgresql.org/docs/13/plpython-util.html
    def debug(self, msg: str, **kwargs: Any) -> None:
        ...

    def log(self, msg: str, **kwargs: Any) -> None:
        ...

    def info(self, msg: str, **kwargs: Any) -> None:
        ...

    def notice(self, msg: str, **kwargs: Any) -> None:
        ...

    def warning(self, msg: str, **kwargs: Any) -> None:
        ...

    def error(self, msg: str, **kwargs: Any) -> None:
        ...

    def fatal(self, msg: str, **kwargs: Any) -> None:
        ...

    def Error(self, msg: str) -> None:
        return self.error(msg)

    def Fatal(self, msg: str) -> None:
        return self.fatal(msg)

    def quote_ident(self, string: str) -> None:
        ...

    def quote_nullable(self, string: str) -> None:
        ...

    def quote_literal(self, string: str) -> None:
        ...


class PLyEnviron(enum.Enum):
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
