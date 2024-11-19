from snowflake import SnowflakeGenerator
from discord_webhook import DiscordWebhook, DiscordEmbed
from discord import Embed

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



def send_webhook_message(url: str, content: str, embed: Embed = None, embeds: list[Embed] = None):
    if embeds and embed:
        raise ValueError("Cannot have both embed and embeds in the same message")
    
    if embed:
        embeds = [embed]
    
    embeds = [embed.to_dict() for embed in embeds]
    
    webhook = DiscordWebhook(url=url, content=content, embeds=embeds)
    
    try:
        webhook.execute()
    except Exception as e:
        print(f"Error sending webhook message: {e}")
        return False
    return True
