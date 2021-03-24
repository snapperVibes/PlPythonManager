import ast
import datetime as dt
import decimal
import inspect
import textwrap
from collections import OrderedDict
from functools import partial
from typing import (
    Dict,
    Any,
    Callable,
    List,
    NoReturn,
    Sequence,
    Union,
    Type,
    OrderedDict as OrderedDictType,
    Optional,
    Tuple,
)

from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy import inspection, exc, text
from sqlalchemy.sql.sqltypes import (
    NULLTYPE,
    BOOLEANTYPE,
    Integer,
    Float,
    Numeric,
    Interval,
    Date,
    DateTime,
    Time,
    Unicode,
    LargeBinary,
)


# Temp home for the mock plpy
plpy: Dict = {}


class PlpyMan:
    def __init__(self) -> None:
        self._funcs: List[Callable] = []

    def plpy_func(
        self,
        func: Callable[..., Any],
        # ret_type: ... = ...
    ) -> Callable[..., NoReturn]:
        """
        Decorator that registers a PlPython Function

        Functions wrapped by plpy_func do not execute on the web server.
        Instead, the function can be called from the database as a PlPython function.
        """
        self._funcs.append(func)

        def wrapper(*args: Any, **kwargs: Any) -> NoReturn:
            raise TypeError(
                f"{func.__name__} was registered as a plpy_func. "
                f"This means that only the database can run this function.\n\n"
                f"Were you trying to write a function that both "
                f"this script AND Plpython could accesses?\n"
                f"Instead of decorating {func.__name__} with plpy_func, "
                f"use something like `plpy_man.to_gd({func.__name__})`. "
                f"Then you can access this function in the GD of plpy functions while "
                f"still being able to call this function normally."
            )

        return wrapper


_default_manager = PlpyMan()


# Use the script sync_docstrings.py to keep these up to date
plpy_func = partial(PlpyMan.plpy_func, _default_manager)


def _dedent(string: str):
    lines = []
    for line in string.splitlines():
        if line.startswith("        "):
            line = line[4:]
        lines.append(line)
    return "\n".join(lines)


def _inspect_function(func: Callable) -> Dict[str, Any]:

    lines = inspect.getsource(func)
    source = textwrap.dedent(lines)
    _ast = ast.parse(source)
    _func_body = _ast.body[0].body
    segments = []
    for segment in _func_body:
        segments.append(_dedent(ast.get_source_segment(source, segment)))
    func_body = "\n".join(segments)

    code = func.__code__
    func_name: str = code.co_name
    # Todo: You could mess this up with something like def why(x): z = x; del(x); return z
    func_args: Tuple[str, ...] = code.co_varnames[: code.co_argcount]
    func_annotations: Dict[str, Any] = func.__annotations__

    return {
        "name": func_name,
        "args": func_args,
        "annotations": func_annotations,
        "body": func_body,
    }


# Local copy of SQLAlchemy's private type map
# Copyright (C) 2005-2021 the SQLAlchemy authors and contributors
_type_map = {
    int: Integer(),
    float: Float(),
    bool: BOOLEANTYPE,
    decimal.Decimal: Numeric(),
    dt.date: Date(),
    dt.datetime: DateTime(),
    dt.time: Time(),
    dt.timedelta: Interval(),
    type(None): NULLTYPE,
    bytes: LargeBinary(),
    str: Unicode(),
}

Type_ = Union[TypeEngine, str, Any]


def to_sql(
    func: Callable[..., Any],
    argtypes: Sequence[Type_] = (),
    rettype: Type_ = "",
) -> text:
    class ListAppender(list):
        def __call__(self, *args: Any) -> None:
            [self.append(arg) for arg in args]

    SQL_INDENT = "  "  # 2 spaces
    PY_INDENT = "    "  # 4 spaces
    SPACE = " "  # Single Space
    NL = "\n"

    # Inspect code to get source
    func_parts = _inspect_function(func)
    name = func_parts["name"]
    args = func_parts["args"]
    annotations = func_parts["annotations"]
    body = func_parts["body"]

    name_clause = f"CREATE OR REPLACE FUNCTION {name}"

    # Argument Clause
    _argtypes: List[str] = []
    if argtypes:
        for t in argtypes:
            _argtypes.append(_stringify_type(t))
    else:
        # Get arg types from type annotations
        for arg in args:
            if arg not in annotations:
                raise ValueError(
                    f"{name} is not fully type annotated. "
                    f"You can also use pass annotations types to plpy_func as SQLAlchemy Types "
                    f"or string literals."
                )
            _annotated_type = annotations[arg]
            try:
                _type = _type_map[_annotated_type]
            except KeyError as err:
                err.args = [
                    f"{_annotated_type} could not be coerced to a Postgresql type. "
                    f"Try passing the SQLAlchemy type (or a string literal) to plpy_func instead."
                ]
                raise err
            _argtypes.append(str(_type))
    args_and_types: List[Tuple[str, str]]
    args_and_types = [(name, _type) for name, _type in zip(args, _argtypes)]
    _arg_string = ", ".join(
        [(lambda arg, _type: f"{arg} {_type}")(*item) for item in args_and_types]
    )
    argument_clause = "".join(f"({_arg_string})")

    _return_type: str
    if rettype:
        _return_type = _stringify_type(rettype)
    else:
        # Get return type from type annotations
        if "return" not in annotations:
            raise ValueError(
                f"{name}'s return value is not type annotated. "
                f"You can also use pass annotations to plpy_func as SQLAlchemy Types "
                f"or string literals."
            )
        _annotated_type = annotations["return"]
        try:
            if _annotated_type is not None:
                _return_type = _type_map[_annotated_type]
            else:
                _return_type = ""
        except KeyError as err:
            err.args = [
                f"{_annotated_type} could not be coerced to a Postgresql type. "
                f"Try passing the SQLAlchemy type (or a string literal) to plpy_func instead."
            ]
            raise err
    return_clause = f"RETURNS {_return_type}" if _return_type else ""
    as_clause = f"AS $$"
    language_clause = "$$ LANGUAGE plpython3u;"

    s = ListAppender()
    s(name_clause)
    if args:
        s(SPACE)
    s(argument_clause)
    if return_clause:
        s(NL)
        s(SQL_INDENT, return_clause, NL)
    else:
        s(SPACE)
    s(as_clause, NL)
    s(textwrap.indent(body, PY_INDENT), NL)
    s(language_clause, NL)

    return text("".join(s))


def _stringify_type(_type: Type_) -> str:
    if callable(_type):
        return str(_type())
    return str(_type)
