import sys
import os

# 1. Force Python to find your folders immediately
PROJECT_DIR = '/storage/emulated/0/Download/CreaturesDominionBot'
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database.db_manager import init_db 

# Import all the persistent button views here
from cogs.factions import FactionButtons
from cogs.verification import VerifyButton
from cogs.tickets import TicketLandingView, CloseTicketView
from cogs.giveaways import GiveawayJoinView

load_dotenv(os.path.join(PROJECT_DIR, '.env'))
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True

class CreaturesDominionBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        # ⚠️ CRUCIAL FIX: Unload the built-in help command to stop the crash!
        self.remove_command('help')

    async def setup_hook(self):
        # Register the buttons so they stay active forever
        self.add_view(FactionButtons())
        self.add_view(VerifyButton())
        self.add_view(TicketLandingView())
        self.add_view(CloseTicketView())
        self.add_view(GiveawayJoinView())

        cogs_dir = os.path.join(PROJECT_DIR, 'cogs')
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py'):
                cog_name = f'cogs.{filename[:-3]}'
                try:
                    await self.load_extension(cog_name)
                    print(f'Loaded: {cog_name}')
                except Exception as e:
                    print(f'Failed to load {cog_name}: {e}')

    async def on_ready(self):
        init_db()  
        print(f'Bot is online! Logged in as {self.user.name}')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # Diagnostic print to check mobile connectivity
        print(f"👉 RAW TEXT SEEN: {message.author.name} sent '{message.content}'")
        await self.process_commands(message)

async def main():
    bot = CreaturesDominionBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    os.chdir(PROJECT_DIR)
    asyncio.run(main())
