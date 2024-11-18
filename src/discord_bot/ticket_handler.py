from discord import Embed, CategoryChannel, Bot
from utils.validator import TicketUser
from utils.settings import guild_settings
import os





class TicketManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.category_ids = []
        self.guild = None


    def append_category_id(self, category_id: int):
        self.category_ids.append(category_id)
        guild_settings.update_settings({ 
            "ticket_opening_categories": self.category_ids
         })

    def initialize(self) -> None:
        guild_id = os.getenv("GUILD_ID")
        if not guild_id:
            raise ValueError("GUILD_ID environment variable is not set.")
        
        self.guild = self.bot.get_guild(int(guild_id))
        if not self.guild:
            raise ValueError(f"Guild with ID {guild_id} not found.")
        
        self.support_team_role = self.guild.get_role(guild_settings.support_team_role_id)
        if not self.support_team_role:
            raise ValueError("Support team role not found in the guild.")
        
        self.category_ids = guild_settings.ticket_opening_categories


    async def get_ticket_category_id(self):
        if not self.guild:
            raise ValueError("Guild not initialized. Call `initialize` first.")
        
        for category_id in self.category_ids:
            category = self.guild.get_channel(category_id)
            if category and len(category.text_channels) < 50:
                return category
        
        # Clone a category if all categories are full
        category_to_clone: CategoryChannel = self.guild.get_channel(self.category_ids[0])
        if not category_to_clone:
            raise ValueError("No valid category found to clone.")
        
        category = await category_to_clone.clone(name=f"Ticket Category - {len(self.category_ids) + 1}")
        self.append_category_id(category.id)
        return category


    async def create_ticket(
        self, title: str, description: str, user: TicketUser
    ) -> int:
        if not self.guild:
            raise ValueError("Guild not initialized. Call `initialize` first.")

        category = await self.get_ticket_category_id()
        channel = await category.create_text_channel(
            name=f"{user.username}-ticket",
            topic=f"Ticket for {user.username}",
        )

        embed = Embed(
            title="Ticket Information",
            description=f"Title: ``{title}``\nDescription: ``{description}``"
        )
        embed.add_field(
            name="User Information",
            value=f"Username: ``{user.username}``\nEmail: ``{user.email}``\nID: ``{user.id}``"
        )
        embed.set_footer(text=self.guild.name)
        embed.set_author(
            name="Ticket System",
            icon_url=self.guild.icon.url if self.guild.icon else None
        )


        await channel.send(
            content=f"{self.support_team_role.mention} A new ticket has been opened. Please review the details below.",
            embed=embed
        )
        
        webhook = await channel.create_webhook(name=user.username, reason="Ticket webhook")

        return channel.id, webhook.url