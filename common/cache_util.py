import datetime as dt

_memory_cache = {}


def memory_cache(cache_time_delta):
    def cache_decorator(func):
        def func_wrapper(*args, **kwargs):
            cache_key = (func.__name__, args, frozenset(kwargs.items()))
            if cache_key in _memory_cache:
                cache_time, cache_val = _memory_cache[cache_key]
                if dt.datetime.now() - cache_time < cache_time_delta:
                    return cache_val

            rval = func(*args, **kwargs)
            _memory_cache[cache_key] = (dt.datetime.now(), rval)
            return rval

        return func_wrapper

    return cache_decorator
