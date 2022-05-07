import time


def time_function(func):
    """Decorator that times functions."""

    async def time_func(*args, **kwargs):
        start = time.time()
        response = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end-start}s")
        return response

    return time_func
