import sys
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

# 1. Automatically detect paths between Android and Render Cloud
if os.path.exists('/storage/emulated/0/Download/CreaturesDominionBot'):
    PROJECT_DIR = '/storage/emulated/0/Download/CreaturesDominionBot'
elif os.path.exists('/storage/emulated/0/CreaturesDominionBot'):
    PROJECT_DIR = '/storage/emulated/0/CreaturesDominionBot'
else:
    PROJECT_DIR = os.getcwd()

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# 2. Safe Database Import
from db_manager import init_db

# 3. Detect folder capitalization (Cogs vs cogs) automatically
COG_FOLDER = 'Cogs' if os.path.exists(os.path.join(PROJECT_DIR, 'Cogs')) else 'cogs'

# 4. Import all persistent button views dynamically
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

# ====================================================================
# BOT ENGINES & ACTIONS
# ====================================================================

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@bot.event
async def setup_hook():
    """Triggered automatically right before the bot logs into Discord."""
    # Register the persistent views
    bot.add_view(FactionButtons())
    bot.add_view(VerifyButton())
    bot.add_view(TicketLandingView())
    bot.add_view(CloseTicketView())
    bot.add_view(GiveawayJoinView())

    # Load all extension scripts from the folder dynamically
    cogs_dir = os.path.join(PROJECT_DIR, COG_FOLDER)

    if os.path.exists(cogs_dir):
        print("PROJECT DIR:", PROJECT_DIR)
        print("COG FOLDER:", COG_FOLDER)
        print("COG FILES:", os.listdir(cogs_dir))

        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                cog_name = f'{COG_FOLDER}.{filename[:-3]}'
                try:
                    await bot.load_extension(cog_name)
                    print(f'✅ Successfully Loaded: {cog_name}')
                except Exception as e:
                    print(f'❌ CRITICAL FAILURE loading {cog_name}: {e}')
                    raise e

@bot.event
async def on_ready():
    """Triggered automatically when the connection succeeds."""
    init_db()
    
    # Broadcast an active visible green status presence immediately
    await bot.change_presence(
        status=discord.Status.online, 
        activity=discord.Game(name="!help | Creatures of Dominion")
    )
    
    print("=" * 50)
    print(f'🚀 SYSTEM LIVE: Bot is completely online!')
    print(f'Logged in as: {bot.user.name} (ID: {bot.user.id})')
    print("=" * 50)

@bot.event
async def on_message(message):
    """Triggered on every message sent across visible chat channels."""
    if message.author == bot.user:
        return
    print(f"RAW TEXT SEEN: {message.author.name} sent '{message.content}'")
    await bot.process_commands(message)

# ====================================================================
# CUSTOM HELP COMMAND SYSTEM
# ====================================================================

@bot.command(name="help")
async def custom_help(ctx):
    """Displays an itemized, organized list of all active tools."""
    embed = discord.Embed(
        title="⚔️ Creatures of Dominion - Help Menu ⚔️",
        description="Use the prefix `!` before any command. Here is a full list of everything I can do:",
        color=discord.Color.gold()
    )
    
    # 1. Info & General
    embed.add_field(
        name="ℹ️ General & Info", 
        value="`!help` | `!ping` | `!about` | `!rules` | `!website` | `!server` | `!userinfo` | `!avatar`", 
        inline=False
    )
    
    # 2. Factions & Lore
    embed.add_field(
        name="🏰 Factions, Lore & Map", 
        value="`!join` | `!leave` | `!role` | `!factions` | `!humans` | `!dragons` | `!creatures` | `!lore` | `!roadmap` | `!territories` | `!map`", 
        inline=False
    )
    
    # 3. Gameplay & Economy
    embed.add_field(
        name="💰 Economy & RPG Features", 
        value="`!profile` | `!rank` | `!xp` | `!daily` | `!balance` | `!work` | `!hunt` | `!shop` | `!buy` | `!sell` | `!quests` | `!bonding`", 
        inline=False
    )
    
    # 4. Community & Utility
    embed.add_field(
        name="🎉 Community & Engagement", 
        value="`!suggest` | `!bug` | `!poll` | `!ticket` | `!close` | `!event` | `!giveaway` | `!verify` | `!updates`", 
        inline=False
    )
    
    # 5. Staff & Admin (Visible to authorized members only)
    if ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator:
        embed.add_field(
            name="🛠️ Staff & Moderation", 
            value="`!warn` | `!warnings` | `!clearwarnings` | `!kick` | `!ban` | `!unban` | `!mute` | `!unmute` | `!timeout` | `!purge` | `!lock` | `!unlock`", 
            inline=False
        )
        embed.add_field(
            name="⚙️ Bot Administration", 
            value="`!setup` | `!setup_factions` | `!config` | `!announce` | `!embed` | `!reload` | `!shutdown`", 
            inline=False
        )
    
    embed.set_footer(text="Creatures of Dominion Bot • Core Systems Fully Operational")
    await ctx.send(embed=embed)

# ====================================================================
# CORE RUNTIME ENGINE RUNTIME SWITCH
# ====================================================================

async def main():
    keep_alive()  # Start the background web server for Render
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    if PROJECT_DIR != os.getcwd():
        os.chdir(PROJECT_DIR)
    asyncio.run(main())
