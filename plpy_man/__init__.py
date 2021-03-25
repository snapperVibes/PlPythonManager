"""
Some Python functions are shared between the server and database.
To avoid repeating code (and accidentally ending up with different implementations),
shared functions are added to the PlPython3u Global Dictionary.
The functions are then callable from PlPython3u by using `GD["func_name"](arguments)`
"""
__all__ = ["to_gd", "plpy_func", "flush", "manager", "mocks"]

from functools import wraps
from typing import Any, Callable, Optional, Sequence, NoReturn

from sqlalchemy.orm import Session

from .manager import PlpyMan, Type_
from . import mocks


_default_manager = PlpyMan()


@wraps(PlpyMan.to_gd)
def to_gd(obj: Any) -> None:
    return _default_manager.to_gd(obj)


@wraps(PlpyMan.plpy_func)
def plpy_func(
    func: Callable[..., Any],
    argtypes: Optional[Sequence[Type_]] = None,
    rettype: Type_ = "",
) -> Callable[..., NoReturn]:
    return _default_manager.plpy_func(func, argtypes, rettype)


@wraps(PlpyMan.flush)
def flush(db: Session) -> None:
    return _default_manager.flush(db)


__cake__ = "\u2728 \U0001f9b8\u200d\u2642\ufe0f \u2728"
