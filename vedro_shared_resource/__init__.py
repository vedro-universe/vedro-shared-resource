from asyncio import iscoroutinefunction
from functools import lru_cache
from typing import Callable, ParamSpec, TypeVar, cast

from async_lru import alru_cache

__all__ = ("shared_resource",)
__version__ = "0.0.1"

P = ParamSpec("P")
R = TypeVar("R")


def shared_resource(*,
                    max_instances: int = 128,
                    type_sensitive: bool = False
                    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def wrapper(func: Callable[P, R]) -> Callable[P, R]:
        if iscoroutinefunction(func):
            return cast(Callable[P, R],
                        alru_cache(maxsize=max_instances, typed=type_sensitive)(func))
        else:
            return cast(Callable[P, R],
                        lru_cache(maxsize=max_instances, typed=type_sensitive)(func))
    return wrapper
