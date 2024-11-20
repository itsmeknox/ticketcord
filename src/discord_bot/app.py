from discord.ext import commands
import discord
import os
import threading
import asyncio
import threading

from .ticket_handler import TicketManager, TranscriptView
from .message_handler import MessageHandler
from chat_exporter import export

from database.tickets import update_ticket_status, fetch_ticket
from socket_manager.send_events import ticket_close_event
from utils.enums import TicketStatus


bot = commands.Bot(intents=discord.Intents.all())
ticket_manager = TicketManager(bot=bot)

is_running = threading.Event()

bot_lock = threading.Lock()

def bot_run_async_coroutine(coro):
    """
    Runs a coroutine object on the bot's event loop.
    
    Args:
        coro (coroutine): The coroutine object to execute.
        
    Returns:
        Any: The result of the coroutine, or raises an exception if it fails.
    """
    with bot_lock:
        future = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            return future.result(timeout=10)  # Adjust timeout as needed
        except Exception as e:
            raise e


    


@bot.event
async def on_ready():
    global is_running
    print(f"Succesfully logged in as {bot.user}")
    ticket_manager.initialize()
    is_running.set()
    
    bot.add_view(TranscriptView())


@bot.slash_command(name="delete_ticket")
async def delete_ticket(ctx: discord.ApplicationContext, reason: str):
    # Remove the first query to fetch the ticket
    # ticket = fetch_ticket(ctx.interaction.channel.id)
    # if not ticket:
    #     await ctx.respond(f"This channel is not a ticket channel.", ephemeral=True)
    
    # Update the ticket status and get the updated ticket
    ticket = update_ticket_status(ctx.interaction.channel_id, TicketStatus.CLOSED)
    if not ticket:
        await ctx.respond(f"Failed to update ticket status in database", ephemeral=True)
        return

    ticket_close_event(ticket.user_id, ticket.id)
        
    await ctx.respond(embed=discord.Embed(title="Ticket Closed", description="This ticket has been closed deleting..."))
    
    transcript_file = await export(ctx.interaction.channel)
    await ticket_manager.send_transcript(ticket, transcript_file, reason)
    await ctx.interaction.channel.delete()

    

@bot.slash_command(name="delete_all_channels_in_category")
async def create_ticket(ctx: discord.ApplicationContext):
    await ctx.respond("Deleting the tickets")
    channels = ctx.interaction.channel.category.channels
    
    for channel in channels:
        await channel.delete()
          


bot.add_cog(MessageHandler(bot))

def run_bot():
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN is not set in the environment variables")
    
    def run():
        bot.run(BOT_TOKEN)
    
    threading.Thread(target=run, daemon=True).start()
    is_running.wait()
