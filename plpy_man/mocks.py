import enum
from typing import Dict, TypedDict, overload

# https://www.postgresql.org/docs/13/plpython-sharing.html
SD: Dict = {}
GD: Dict = {}


# https://www.postgresql.org/docs/13/plpython-trigger.html
class _TD(TypedDict):
    event: str
    when: str
    level: str
    new: Dict
    old: Dict
    name: str
    table_schema: str
    relid: str
    args: str


TD = _TD()


class plpy:
    """ Mocked plpy class that is automatically imported by methods on Plpy"""

    # https://www.postgresql.org/docs/13/plpython-database.html
    @overload
    def execute(self, query: str, max_rows=None):
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

    def log(self, msg, *args, **kwargs):
        pass

    def info(self, msg, *args, **kwargs):
        pass

    def notice(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def fatal(self, msg, *args, **kwargs):
        pass

    def quote_ident(self, string):
        pass

    def quote_nullable(self, string):
        pass

    def quote_literal(self, string):
        pass


class PLyPlan:
    def cursor(self, **kwargs):
        pass

    def execute(self, **kwargs):
        pass

    def status(self, **kwargs):
        pass


class PLyResult:
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


class PlpyEnv(enum.Enum):
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
