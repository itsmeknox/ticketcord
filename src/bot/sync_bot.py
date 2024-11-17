
import requests
import time
import logging
import threading
import json

from typing_extensions import Literal, Dict, Union, Optional, List
from discord.errors import HTTPException, Forbidden, NotFound, DiscordServerError


API_VERSION: int = 10


__all__ = (
    "Client"
)

logger = logging.getLogger("discord_wrapper")


class Route:
    def __init__(self, method: Literal["PUT", "POST", "GET", "DELETE"], endpoint: str, **kwargs):
        if method not in ["PUT", "POST", "GET", "DELETE"]:
            raise ValueError("Method must be one of PUT, POST, GET, or DELETE")

        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        self.method = method
        self.endpoint = endpoint

    @property
    def url(self):
        return f"https://discord.com/api/v{API_VERSION}/{self.endpoint}"


class SyncBot:
    def __init__(self, token: str):
        self.token: str = token
        self.global_lock = threading.Lock()
        self.global_rate_limit_reset: float = 0

    def request(self, route: Route, payload: Optional[Dict[str, Union[str, int, float, list, dict]]] = None, **kwargs) -> dict:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bot {self.token}"

        # Check if the json parameter is valid JSON
        if payload is not None:
            try:
                json.dumps(payload)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid JSON data: {e}")

        # Global rate limit check with lock
        with self.global_lock:
            if time.time() < self.global_rate_limit_reset:
                wait_time = self.global_rate_limit_reset - time.time()
                logger.debug(
                    f"Global rate limit active. Waiting {wait_time:.2f} seconds.")
                time.sleep(wait_time)

        for tries in range(3):
            try:
                response = requests.request(
                    route.method, route.url, headers=headers, json=payload, **kwargs)
            except requests.RequestException as e:
                raise RuntimeError(f"Network request failed: {e}")

            if 200 <= response.status_code < 300:
                try:
                    return response.json()
                except ValueError:
                    raise HTTPException("Invalid JSON response")

            # Retry on server error (500-series)
            if response.status_code in {500, 502, 503, 504}:
                wait_time = 3 * (2 ** tries)  # Exponential backoff
                logger.debug(
                    f"Server error {response.status_code}, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            # Handle 429 rate limit
            if response.status_code == 429:
                retry_after = max(response.json().get("retry_after", 5), 0)
                is_global = response.json().get("global", False)

                if is_global:
                    # Set global rate limit reset time and lock
                    self.global_rate_limit_reset = time.time() + retry_after
                    logger.warning(
                        f"Global rate limit hit, retrying in {retry_after} seconds.")

                    with self.global_lock:
                        time.sleep(retry_after)
                    logger.debug(
                        "Global rate limit period ended, resuming requests.")
                else:
                    logger.debug(
                        f"Bucket-specific rate limit hit, retrying in {retry_after} seconds.")
                    time.sleep(retry_after)
                continue
            
            print(response.json())
            # Handle client-side error cases
            if response.status_code == 403:
                raise Forbidden(response)

            elif response.status_code == 404:
                raise NotFound(response)

            elif response.status_code >= 500:
                raise DiscordServerError(response)

            else:
                raise HTTPException(response)

        raise RuntimeError("Failed to make request to Discord after retries")

    def create_text_channel(self, guild_id: int, name: str, topic: str = None, category_id: int = None) -> dict:
        route = Route("POST", f"guilds/{guild_id}/channels")
        payload = {
            "name": name,
            "type": 0,
            "topic": topic,
            "parent_id": category_id
        }
        return self.request(route, payload=payload)

    def create_text_channel(
            self,
            guild_id: int,
            name: str,
            topic: str = None,
            rate_limit_per_user: int = None,
            position: int = None,
            category_id: int = None,
            nsfw: bool = False,
            **options
    ) -> dict:
        if len(name) > 100:
            raise ValueError("Channel name must be less than 100 characters")

        if topic and len(topic) > 1024:
            raise ValueError("Channel topic must be less than 1024 characters")

        if rate_limit_per_user and not (0 <= rate_limit_per_user <= 21600):
            raise ValueError(
                "Rate limit per user must be between 0 and 21600 seconds")

        if position is not None and position < 0:
            raise ValueError("Position must be a positive integer")

        if category_id is not None and category_id < 0:
            raise ValueError("Category ID must be a positive integer")

        if not isinstance(nsfw, bool):
            raise ValueError("NSFW must be a boolean")

        payload = {
            "type": 0,
            "name": name,
            "topic": topic,
            "rate_limit_per_user": rate_limit_per_user,
            "position": position,
            "parent_id": category_id,
            "nsfw": nsfw,
        }
        

        # Remove None values from the payload
        payload = {key: value for key, value in payload.items() if value is not None}

        return self.request(Route("POST", f"guilds/{guild_id}/channels"), payload=payload)

    def get_channels(self, guild_id: int) -> List[dict]:
        return self.request(Route("GET", f"guilds/{guild_id}/channels"))


    def get_category_channels(self, guild_id: int, category_id: int) -> dict:
        channels = self.get_channels(guild_id=guild_id)
        category_channels = [channel for channel in channels if channel.get("parent_id") == str(category_id)]
        return category_channels


    def get_available_ticket_category(self, categories: List[str], guild_id: str) -> Optional[int]:
        MAX_CHANNELS_PER_CATEGORY = 50

        # Iterate through each category ID
        channels = self.get_channels(guild_id=guild_id)
        for category_id in categories:
            channels_in_category = [channel for channel in channels if channel.get("parent_id") == str(category_id)]

            if len(channels_in_category) < MAX_CHANNELS_PER_CATEGORY:
                return category_id

        return None