import sys
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 1. Automatically detect paths between Android and Render Cloud
if os.path.exists('/storage/emulated/0/Download/CreaturesDominionBot'):
    PROJECT_DIR = '/storage/emulated/0/Download/CreaturesDominionBot'
elif os.path.exists('/storage/emulated/0/CreaturesDominionBot'):
    PROJECT_DIR = '/storage/emulated/0/CreaturesDominionBot'
else:
    PROJECT_DIR = os.getcwd()  # This runs perfectly on Render

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# 2. Safe Database Import
from db_manager import init_db

# 3. Detect folder capitalization (Cogs vs cogs) automatically to prevent errors
COG_FOLDER = 'Cogs' if os.path.exists(os.path.join(PROJECT_DIR, 'Cogs')) else 'cogs'

# 4. Import all persistent button views using dynamic import paths
factions = __import__(f"{COG_FOLDER}.factions", fromlist=["FactionButtons"])
FactionButtons = factions.FactionButtons

verification = __import__(f"{COG_FOLDER}.verification", fromlist=["VerifyButton"])
VerifyButton = verification.VerifyButton

tickets = __import__(f"{COG_FOLDER}.tickets", fromlist=["TicketLandingView", "CloseTicketView"])
TicketLandingView = tickets.TicketLandingView
CloseTicketView = tickets.CloseTicketView

giveaways = __import__(f"{COG_FOLDER}.giveaways", fromlist=["GiveawayJoinView"])
GiveawayJoinView = giveaways.GiveawayJoinView

# 5. Load environment variables securely
load_dotenv(os.path.join(PROJECT_DIR, '.env'))
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class CreaturesDominionBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.remove_command('help')

    async def setup_hook(self):
        # Register the persistent views
        self.add_view(FactionButtons())
        self.add_view(VerifyButton())
        self.add_view(TicketLandingView())
        self.add_view(CloseTicketView())
        self.add_view(GiveawayJoinView())

        # Load all extension scripts from the folder dynamically
        cogs_dir = os.path.join(PROJECT_DIR, COG_FOLDER)
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    cog_name = f'{COG_FOLDER}.{filename[:-3]}'
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
        print(f"RAW TEXT SEEN: {message.author.name} sent '{message.content}'")
        await self.process_commands(message)
    # Add this custom help command under your bot class event handlers
    @commands.command(name="help")
    async def custom_help(self, ctx):
        """Displays a clean list of all available bot commands."""
        embed = discord.Embed(
            title="⚔️ Creatures of Dominion - Help Menu ⚔️",
            description="Welcome! Here is a list of all available command modules for the bot. Use `!help <module>` for specific info.",
            color=discord.Color.gold()
        )
        
        # List all the active cog systems you have installed
        embed.add_field(name="🏰 Core Systems", value="`!factions` | `!territory` | `!quests` | `!leveling` | `!economy`", inline=False)
        embed.add_field(name="🎲 Fun & Games", value="`!fun` | `!giveaways` | `!creatures` | `!dragons`", inline=False)
        embed.add_field(name="🛠️ Server Tools", value="`!moderation` | `!tickets` | `!verification` | `!suggestions`", inline=False)
        
        embed.set_footer(text="Creatures of Dominion Bot • Use prefix '!'")
        await ctx.send(embed=embed)

async def main():
    bot = CreaturesDominionBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    # Safely switch directory only if running on Android device
    if PROJECT_DIR != os.getcwd():
        os.chdir(PROJECT_DIR)
    asyncio.run(main())
