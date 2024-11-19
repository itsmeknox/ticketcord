from snowflake import SnowflakeGenerator
from discord_webhook import DiscordWebhook, DiscordEmbed
from discord import Embed

from typing import List, Optional, Union

import threading
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


def send_webhook_message(
    url: str,
    content: Optional[str] = None,
    embed: Optional[Embed] = None,
    embeds: Optional[List[Embed]] = None,
    run_as_thread: bool = False
) -> Union[bool, threading.Thread]:
    """
    Sends a message to a Discord webhook with optional embeds, either synchronously or in a separate thread.

    Args:
        url (str): The Discord webhook URL.
        content (Optional[str]): The main content of the message (default: None).
        embed (Optional[DiscordEmbed]): A single Discord embed (mutually exclusive with `embeds`).
        embeds (Optional[List[DiscordEmbed]]): A list of Discord embeds (mutually exclusive with `embed`).
        run_as_thread (bool): Whether to send the message in a separate thread (default: False).

    Returns:
        Union[bool, threading.Thread]: Returns True if the message was sent successfully, or the thread object if `run_as_thread` is True.
    """

    def send() -> bool:
        """
        Internal function to send the webhook message.
        """
        # Validate input: Cannot have both `embed` and `embeds`
        if embed and embeds:
            raise ValueError("Cannot provide both `embed` and `embeds`.")

        # Prepare the embed list
        embeds_list = [embed] if embed else (embeds or [])
        embeds_data = [embed.to_dict() for embed in embeds_list]

        # Create the webhook object
        webhook = DiscordWebhook(url=url, content=content)
        for embed_data in embeds_data:
            webhook.add_embed(embed_data)

        try:
            response = webhook.execute()
            if response.status_code != 200:
                print(f"Webhook failed with status code {response.status_code}: {response.content}")
                return False

        except Exception as e:
            print(f"Error sending webhook message: {e}")
            return False

        return True

    # Run in a thread if requested
    if run_as_thread:
        thread = threading.Thread(target=send, daemon=True)
        thread.start()
        return thread

    # Run synchronously
    return send()



