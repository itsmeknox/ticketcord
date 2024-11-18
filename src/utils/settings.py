from .mongo_client import get_database

class Settings:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["settings"]
        self._initialize()

    def _initialize(self):
        self.load_settings()
        self._validate_settings()

    def _validate_settings(self):
        if not self.bot_token:
            raise ValueError("Bot token is not set")
        
        if not self.guild_id:
            raise ValueError("Guild ID is not set")
        
        if not isinstance(self.ticket_opening_category, list) or not self.ticket_opening_category:
            raise ValueError("Ticket opening category is not set")
        
        if not self.ticket_closing_category:
            raise ValueError("Ticket closing category is not set")
        
        if not self.ticket_transcript_channel:
            raise ValueError("Ticket transcript channel is not set")
        
        if not self.server_log_channel:
            raise ValueError("Server log channel is not set")
        
        return True

    def load_settings(self):
        data = self.collection.find_one({"id": "settings"})
        if not data:
            raise ValueError("Settings not found in the database")
        
        self.bot_token: str = data["bot_token"]
        self.guild_id: int = data["guild_id"]
        self.ticket_opening_category: list = data["ticket_opening_category"]
        self.ticket_closing_category: int = data["ticket_closing_category"]
        self.ticket_transcript_channel: int = data["ticket_transcript_channel"]
        self.server_log_channel: int = data["server_log_channel"]
        self.support_team_role: int = data["support_team_role"]

    def update_settings(self, data: dict) -> bool:
        self.collection.update_one({"id": "settings"}, {"$set": data})
        self.load_settings()
        return True



settings = Settings()
