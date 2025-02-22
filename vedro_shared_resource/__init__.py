from asyncio import iscoroutinefunction
from functools import lru_cache
from typing import Callable, ParamSpec, TypeVar, cast

from async_lru import alru_cache

__all__ = ("shared_resource",)
__version__ = "0.1.0"

P = ParamSpec("P")
R = TypeVar("R")


def shared_resource(*,
                    max_instances: int = 128,
                    type_sensitive: bool = False
                    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator for caching function call results (memoization).

    This decorator supports both synchronous and asynchronous functions. For synchronous functions,
    it uses ``functools.lru_cache`` to cache results, and for asynchronous functions, it uses
    ``async_lru.alru_cache`` to provide equivalent caching behavior.

    It is useful for sharing expensive-to-compute or frequently accessed resources across multiple
    calls, reducing redundant computations and improving performance.

    :param max_instances: The maximum number of cached results to retain. Once the cache reaches
                          this limit, the least-recently-used entry is evicted. Defaults to 128.
    :param type_sensitive: If True, values of different types (e.g., `1` and `1.0`) are cached
                           separately. Defaults to False.
    :return: A decorator that wraps the target function with caching capabilities.
    """
    def wrapper(func: Callable[P, R]) -> Callable[P, R]:
        if iscoroutinefunction(func):
            return cast(Callable[P, R],
                        alru_cache(maxsize=max_instances, typed=type_sensitive)(func))
        else:
            return cast(Callable[P, R],
                        lru_cache(maxsize=max_instances, typed=type_sensitive)(func))
    return wrapper
