# """
# Some Python functions are shared between the server and database.
# To avoid repeating code (and accidentally ending up with different implementations),
# shared functions are added to the PlPython3u Global Dictionary.
# The functions are then callable from PlPython3u by using `GD["func_name"](arguments)`
# """
# import enum
# import inspect
# import textwrap
# from functools import partial
# from typing import (
#     Sequence,
#     Any,
#     List,
#     Callable,
#     overload,
#     Dict,
#     TypedDict,
#     NoReturn,
#     Optional,
#     NamedTuple,
# )
#
# from sqlalchemy import text
# from sqlalchemy import sql
# from sqlalchemy.orm import Session
#
#
# class PlpyManError(BaseException):
#     """ Exception representing errors resulting from improper use of the plpy_man library """
#
#
# class PlpyMan:
#     def __init__(self) -> None:
#         self._gd: List[Any] = []
#         self._funcs: List[Callable] = []
#
#     def to_gd(self, obj: Any) -> None:
#         """ Registers an object to have its source copied to the PlPython Global Dictionary """
#         self._gd.append(obj)
#
#     def plpy_func(self, func: Callable[..., Any]) -> Callable[..., NoReturn]:
#         """
#         Decorator that registers a PlPython Function
#
#         Functions wrapped by plpy_func do not execute on the web server.
#         Instead, the function can be called from the database as a PlPython function.
#         """
#         self._funcs.append(func)
#
#         def wrapper(*args: Any, **kwargs: Any) -> NoReturn:
#             raise PlpyManError(
#                 f"{func.__name__} was registered as a plpy_func. "
#                 f"This means that only the database can run this function.\n\n"
#                 f"Were you trying to write a function that both "
#                 f"this script AND Plpython could accesses?\n"
#                 f"Instead of decorating {func.__name__} with plpy_func, "
#                 f"use something like `plpy_man.to_gd({func.__name__})`. "
#                 f"Then you can access this function in the GD of plpy functions while "
#                 f"still being able to call this function normally."
#             )
#
#         return wrapper
#
#     def flush(self, db: Session) -> None:
#         self._flush_gd(db)
#         self._flush_funcs(db)
#
#     def _flush_gd(self, db: Session) -> None:
#         source = _prep_source(self._gd)
#         sql = _write_gd_sql(source)
#         db.execute(sql)
#         db.execute("SELECT _add_to_gd()")
#         self._gd = []
#
#     def _flush_funcs(self, db: Session) -> None:
#         for func in self._funcs:
#             sql = _write_plpy_func_sql(func)
#             db.execute(sql)
#         self._funcs = []
#
#
# _default_manager = PlpyMan()
# to_gd = partial(PlpyMan.to_gd, self=_default_manager)
# plpy_func = partial(PlpyMan.plpy_func, self=_default_manager)
# flush = partial(PlpyMan.flush, self=_default_manager)
#
#
# def _prep_source(objs: Sequence[Callable]) -> str:
#     # Keep in mind: "Reflection is never clever." https://go-proverbs.github.io/
#     #  Unfortunately, reflection (introspection) seems like the best way
#     #  to ensure the code on the server and in the database remain identical.
#     source: List[str] = []
#     for obj in objs:
#         source.append(textwrap.dedent(inspect.getsource(obj)))
#         source.append(f'\nGD["{obj.__name__}"] = {obj.__name__}\n\n')
#     return "\n".join(source)[:-1]  # The final extraneous line is trimmed
#
#
# def _write_gd_sql(py_script: str) -> text:
#     return text(
#         f"""\
# CREATE OR REPLACE FUNCTION _add_to_gd()
# RETURNS TEXT AS $$
# {py_script}
# $$ LANGUAGE plpython3u;
# """
#     )
#
#
# def _write_plpython_sql(func: Callable[..., Any]) -> text:
#     pass
#
#
# # def _write_plpy_func_sql(func: Callable[..., Any]) -> text:
# #     class _Argument:
# #         argmode: Optional[str]
# #         argname: Optional[str]
# #         argtype: str
# #         _default_expr: Optional[str]
# #
# #         @property
# #         def default_expr(self):
# #             if self._default_expr:
# #                 return f"= {self._default_expr}"
# #             return None
# #
# #         def __str__(self):
# #             parameters = []
# #             for param in [self.argmode, self.argname, self.argtype, self.default_expr]:
# #                 if param:
# #                     parameters.append(param)
# #             return " ".join(p for p in parameters)
# #
# #     name: str
# #     argument_clause: Sequence[_Argument]
# #     return_clause: ...
# #     # rettype or table
# #     rettype: Optional[str]
# #     # together, repeatable zipped list
# #     columns: Sequence[_Column]
# #     return text(
# #         f"""\
# # CREATE OR REPLACE FUNCTION
# #     {name}( {",".join(str(arg) for arg in argument_clause)} )
# #     {return_clause}
# #
# # """
# #     )
#
#
# ##############################################################################
# # Mocks
# # https://www.postgresql.org/docs/13/plpython-sharing.html
# SD = ...
# GD = ...
#
#
# # https://www.postgresql.org/docs/13/plpython-trigger.html
# class TD(TypedDict):
#     event: str
#     when: str
#     level: str
#     new: Dict
#     old: Dict
#     name: str
#     table_schema: str
#     relid: str
#     args: str
#
#
# class plpy:
#     """ Mocked plpy class that is automatically imported by methods on Plpy"""
#
#     # https://www.postgresql.org/docs/13/plpython-database.html
#     @overload
#     def execute(self, query: str, max_rows=None):
#         pass
#
#     def prepare(self, query, argtypes=None):
#         pass
#
#     def execute(self, plan, arguments=None, max_rows=None):
#         pass
#
#     @overload
#     def cursor(self, query):
#         pass
#
#     def cursor(self, plan, arguments=None):
#         pass
#
#     class SPIError(BaseException):
#         pass
#
#     class spiexceptions:
#         # Todo: There is a lot to unpack here
#         # https://www.postgresql.org/docs/13/errcodes-appendix.html#ERRCODES-TABLE
#         pass
#
#     # https://www.postgresql.org/docs/13/plpython-database.html
#     def commit(self):
#         pass
#
#     def rollback(self):
#         pass
#
#     # https://www.postgresql.org/docs/13/plpython-util.html
#     def debug(self, msg, **kwargs):
#         pass
#
#     def log(self, msg, **kwargs):
#         pass
#
#     def info(self, msg, **kwargs):
#         pass
#
#     def notice(self, msg, **kwargs):
#         pass
#
#     def warning(self, msg, **kwargs):
#         pass
#
#     def error(self, msg, **kwargs):
#         pass
#
#     def fatal(self, msg, **kwargs):
#         pass
#
#     def quote_ident(self, string):
#         pass
#
#     def quote_nullable(self, string):
#         pass
#
#     def quote_literal(self, string):
#         pass
#
#
# class Result:
#     """ Mocked Result returned by plpy.execute """
#
#     def nrows(self):
#         pass
#
#     def status(self):
#         pass
#
#     def colnames(self):
#         pass
#
#     def coltypes(self):
#         pass
#
#     def coltypmods(self):
#         pass
#
#
# class PlpyEnv(enum.Enum):
#     # https://www.postgresql.org/docs/10/plpython-envar.html
#     PYTHONHOME = "PYTHONHOME"
#     PYTHONPATH = "PYTHONPATH"
#     PYTHONY2K = "PYTHONY2K"
#     PYTHONOPTIMIZE = "PYTHONOPTIMIZE"
#     PYTHONDEBUG = "PYTHONDEBUG"
#     PYTHONVERBOSE = "PYTHONVERBOSE"
#     PYTHONCASEOK = "PYTHONCASEOK"
#     PYTHONWRITEBYTECODE = "PYTHONWRITEBYTECODE"
#     PYTHONIOENCODING = "PYTHONIOENCODING"
#     PYTHONUSERBASE = "PYTHONUSERBASE"
#     PYTHONHASHSEED = "PYTHONHASHSEED"
#
#
# __cake__ = "\u2728 \U0001f9b8\u200d\u2642\ufe0f \u2728"
