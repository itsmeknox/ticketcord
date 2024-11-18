from .mongo_client import get_database
import os
from typing_extensions import List
class GuildSettings:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["guild_settings"]
        self._initialize()

    def _initialize(self):
        self.load_settings()
        self._validate_settings()

    def _validate_settings(self): 
        if not isinstance(self.ticket_closing_categories, list) or not self.ticket_closing_categories:
            raise ValueError("Ticket opening category is not set")
        
        if not self.ticket_closing_categories:
            raise ValueError("Ticket closing category is not set")

    def load_settings(self):
        data = self.collection.find_one({"id": "guild_settings"})
        if not data:
            raise ValueError("Settings not found in the database")

        
        self.ticket_opening_categories: List[int] = data["ticket_opening_categories"]
        self.ticket_closing_categories: List[int] = data["ticket_closing_categories"]

    def update_settings(self, data: dict) -> bool:
        self.collection.update_one({"id": "guild_settings"}, {"$set": data})
        self.load_settings()
        return True



guild_settings = GuildSettings()
