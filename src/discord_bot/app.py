from discord.ext import commands
import discord
import os
import threading

from .ticket_handler import TicketManager



bot = commands.Bot(intents=discord.Intents.all())
ticket_manager = TicketManager(bot=bot)

is_running = threading.Event()

@bot.event
async def on_ready():
    global is_running
    is_running.set()
    print(f"Logged in as {bot.user}")
    await ticket_manager.initialize()



def run_bot():
    if BOT_TOKEN := os.getenv("BOT_TOKEN") is None:
        raise ValueError("BOT_TOKEN is not set in the environment variables")
    
    def run():
        bot.run(BOT_TOKEN)
    
    threading.Thread(target=run, daemon=True).start()
    is_running.wait()
