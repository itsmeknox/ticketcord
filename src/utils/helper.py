from snowflake import SnowflakeGenerator
import time
import functools

gen = SnowflakeGenerator(0)


def generate_snowflake_id() -> int:
    return next(gen)

def generate_timestamp() -> int:
    return int(time.time())

def calc_timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Func {func.__name__} took {time.time() - start}s to complete")
        return result
    return wrapper