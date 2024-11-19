from snowflake import SnowflakeGenerator
import time
gen = SnowflakeGenerator(0)


def generate_snowflake_id() -> int:
    return next(gen)

def generate_timestamp() -> int:
    return int(time.time())