from .mongo_client import get_database
from typing_extensions import List
import os


class GuildSettings:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["settings"]
        self._initialize()

    def _initialize(self):
        self.load_settings()
        self._validate_settings()
        
        self.admin_role_id = int(os.getenv("ADMIN_ROLE_ID"))
        self.manager_role_id = int(os.getenv("MANAGER_ROLE_ID"))
        self.developer_role_id = int(os.getenv("DEVELOPER_ROLE_ID"))
        self.support_team_role_id = int(os.getenv("SUPPORT_TEAM_ROLE_ID"))

    def _validate_settings(self): 
        if not isinstance(self.ticket_closing_categories, list) or not self.ticket_closing_categories:
            raise ValueError("Ticket opening category is not set or not a list of integers")
        
        if not isinstance(self.ticket_closing_categories, list) or not self.ticket_closing_categories:
            raise ValueError("Ticket closing category is not set or not a list of integers")



    def load_settings(self):
        data = self.collection.find_one({"id": "guild_settings"})
        if data is None:
            raise ValueError("Settings not found in the database")

        try:
            self.replay_to_success_message: bool = data["replay_to_success_message"]
            self.ticket_opening_categories: List[int] = data["ticket_opening_categories"]
            self.ticket_closing_categories: List[int] = data["ticket_closing_categories"]
        except KeyError:
            raise ValueError("Invalid settings data found in the database")



    def update_settings(self, data: dict) -> bool:
        self.collection.update_one({"id": "guild_settings"}, {"$set": data})
        self.load_settings()
        return True



guild_settings = GuildSettings()
