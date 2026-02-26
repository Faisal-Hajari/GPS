import time
import logging
import functools

logger = logging.getLogger("uvicorn")


def timeit(func=None):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.info(f"{fn.__qualname__} took {elapsed:.4f}s")
            return result

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def cached(maxsize: int = 128):
    def decorator(func):
        cached_func = functools.lru_cache(maxsize=maxsize)(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = cached_func(*args, **kwargs)
            info = cached_func.cache_info()
            total = info.hits + info.misses
            hit_rate = (info.hits / total * 100) if total > 0 else 0.0
            logger.info(
                f"[cache] {func.__qualname__} | hits={info.hits} misses={info.misses} "
                f"hit_rate={hit_rate:.1f}% size={info.currsize}/{info.maxsize}"
            )
            return result

        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear
        return wrapper

    return decorator
