from snowflake import SnowflakeGenerator
from discord_webhook import DiscordWebhook
from discord import Embed, ApplicationContext

from flask import request, Request

from flask_limiter.util import get_remote_address

from typing import List, Optional, Union

import threading
import time
import functools
import os

gen = SnowflakeGenerator(0)

ERROR_WEBHOOK_URL = os.getenv("ERROR_WEBHOOK_URL")
ERROR_BOT_WEBHOOK_URL = os.getenv("ERROR_BOT_WEBHOOK_URL")


def generate_snowflake_id() -> str:
    return str(next(gen))

def generate_timestamp() -> int:
    return int(time.time())

def calc_timing(func):
    @functools.wraps(func)
    def wrapper(*args, kwargs):
        start = time.time()
        result = func(*args, kwargs)
        print(f"Func {func.__name__} took {time.time() - start}s to complete")
        return result
    return wrapper


def send_webhook_message(
    url: str,
    content: Optional[str] = None,
    embed: Optional[Embed] = None,
    embeds: Optional[List[Embed]] = None,
    run_as_thread: bool = False
):
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

    def send():
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
        webhook = DiscordWebhook(url=url, content=content, rate_limit_retry=True)
        for embed_data in embeds_data:
            webhook.add_embed(embed_data)

        try:
            return webhook.execute().status_code in [200, 201, 203, 204]
        except Exception as e:
            print(f"Error sending webhook message: {e}")
            return False


    # Run in a thread if requested
    if run_as_thread:
        thread = threading.Thread(target=send, daemon=True)
        thread.start()
        return thread

    # Run synchronously
    return send()




def rate_limit_handler():
    # Safely retrieve the user ID
    user_id = getattr(request, "user_id", None)  # OR use g.user_id
    if user_id:
        return str(user_id)  # Use user ID for rate limiting
    else:
        return get_remote_address()  # Fallback to IP-based limiting
    
    

def send_disord_error_log(ctx: ApplicationContext, error_type: str, trackback: str, error: Exception):
    trackback_len = len(trackback)
    
    if trackback_len > 4000:
        trackback =  "..... (truncated)\n" + trackback[(trackback_len-4000):]

    embed = Embed(
        title=error_type, 
        description=f"```py\n{trackback}```", 
        color=0xFF0000
    )
    
    if ctx:
        embed.add_field(
            name="Interaction Info",
            value=f"Command Name: ``{ctx.command.name}``\nChannel: ``{ctx.interaction.channel.name}``\nUser: ``{ctx.interaction.user.name}``\nGuild: ``{ctx.interaction.guild.name}``",
            inline=False
        )
    
    embed.add_field(
        name="Error Type",
        value=f"```py\n{error.__class__.__name__}```",
        inline=False
    )

    send_webhook_message(url=ERROR_BOT_WEBHOOK_URL, embed=embed, run_as_thread=True)

def send_error_log(error_type: str, trackback: str, error: Exception):

    trackback_len = len(trackback)
    if trackback_len > 4000:
        trackback =  "..... (truncated)\n" + trackback[(trackback_len-4000):]

    embed = Embed(
        title=error_type, 
        description=f"```py\n{trackback}```", 
        color=0xFF0000
    )
    
    embed.add_field(
        name="Error Type",
        value=f"```py\n{error.__class__.__name__}```",
        inline=False
    )

    embed.add_field(
    name="Request Info",
    value=f"Path: ``{request.path}``\nMethod: ``{request.method}``\nQuery Params: ```py\n{request.args.to_dict()}```",
    inline=False
)   
    request_body = request.data.decode("utf-8") if len(request.data) < 1000 else request.data.decode("utf-8")[:1000] + "..... (truncated)"
    embed.add_field(
        name="Request Body",
        value=f"```py\n{request_body}```",
    )

    user_ip = request.remote_addr

    embed.add_field(
    name="User Info",
    value=f"IP Address: ``{user_ip}``\nUser-Agent: ``{request.headers.get('User-Agent')}``",
    inline=False
)   
    send_webhook_message(
        url=ERROR_WEBHOOK_URL,
        embed=embed,
        run_as_thread=True
    )