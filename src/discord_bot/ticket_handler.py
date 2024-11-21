from discord import Embed, CategoryChannel, Bot
from utils.schema import TicketUser, Ticket
from utils.settings import guild_settings

import chat_exporter
import discord

import os
import io

class TranscriptView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        
    
    @discord.ui.button(label="View Transcript", style=discord.ButtonStyle.primary, custom_id="transcript_button")
    async def send_transcript(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            file_link = await chat_exporter.link(interaction.message)
        except IndexError:
            return await interaction.response.send_message("No transcript found.", ephemeral=True)
        
        await interaction.response.send_message(f"{file_link}", ephemeral=True)

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
        
        self.transcript_channel = self.guild.get_channel(int(os.getenv("TRANSCRIPT_CHANNEL_ID")))
        if not self.transcript_channel:
            raise ValueError("Transcript channel not found in the guild.")
        
        self.critical_category = self.guild.get_channel(int(os.getenv("CRITICAL_TICKET_CATEGORY_ID")))
        if not self.critical_category:
            raise ValueError("Critical ticket category not found in the guild.")
        
        self.urgent_category = self.guild.get_channel(int(os.getenv("URGENT_TICKET_CATEGORY_ID")))
        if not self.urgent_category:
            raise ValueError("Urgent ticket category not found in the guild.")

        
        

        


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
        category.move(category_to_clone.position + 1)

        self.append_category_id(category.id)
        return category
    
    async def send_transcript(self, ticket: Ticket, transcript_str: str, reason: str = None):
        embed = Embed(
            title="Ticket Transcript",
            
        )
        
        embed.add_field(
            name="Ticket Information",
            value=f"Topic: ``{ticket.topic}``\nDescription: ``{ticket.description}``\nStatus: ``{ticket.status.title()}``",
            inline=False
        )
        embed.add_field(
            name="User Information",
            value=f"Name: ``{ticket.username}``\nEmail: ``{ticket.user_email}``\nID: ``{ticket.user_id}``\nRole: ``{ticket.user_role.title()}``",
        )
        if reason:
            embed.add_field(
            name="Reason",
            value=reason,
        )
        embed.set_footer(text=self.guild.name)
        transcript_file = discord.File(
        io.BytesIO(transcript_str.encode()),
        filename=f"transcript-{ticket.id}.html",
    )
        await self.transcript_channel.send(embed=embed, file=transcript_file, view=TranscriptView())



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
            value=f"Username: ``{user.username}``\nEmail: ``{user.email}``\nID: ``{user.id}``\nRole: ``{user.role.title()}``"
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