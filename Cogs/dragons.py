import discord
from discord.ext import commands
import random
import sqlite3
from database.db_manager import DB_PATH, create_profile

# Core Dragon Genome Data Matrix
DRAGON_TEMPLATES = {
    "Fire Drake": {"element": "🔥 Fire", "tier": 1, "emoji": "🔴"},
    "Water Serpent": {"element": "💧 Water", "tier": 1, "emoji": "🔵"},
    "Earth Wyrm": {"element": "⛰️ Earth", "tier": 1, "emoji": "🟤"},
    # Tier 2 Fusion Dragons
    "Steam Leviathan": {"element": "💨 Steam (Fire + Water)", "tier": 2, "emoji": "💨"},
    "Magma Behemoth": {"element": "🌋 Lava (Fire + Earth)", "tier": 2, "emoji": "🌋"},
    "Mud Hydra": {"element": "🌱 Nature (Water + Earth)", "tier": 2, "emoji": "🐊"},
    # Rare Tier 3 Legendary
    "Eclipse Overlord": {"element": "👑 Cosmic Fusion", "tier": 3, "emoji": "✨"}
}

class Dragons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prefix Command: !dragon_index
    @commands.command(name="dragon_index", aliases=["dragons", "dex"])
    async def dragon_index(self, ctx):
        """Displays the entire available dragon genetic pool"""
        embed = discord.Embed(
            title="📜 The Dragon Enclyclopedia",
            description="Discover the genetic paths of the dominion's great beasts! Breed Tier 1 dragons together to unlock hybrid elements.",
            color=0xe67e22
        )
        
        for name, info in DRAGON_TEMPLATES.items():
            embed.add_field(
                name=f"{info['emoji']} {name}",
                value=f"**Element:** {info['element']}\n**Evolution Tier:** Class {info['tier']}",
                inline=True
            )
            
        await ctx.send(embed=embed)

    # Prefix Command: !breed [Dragon 1] [Dragon 2]
    @commands.command(name="breed")
    @commands.cooldown(1, 10, commands.BucketType.user) # Short cooldown for testing
    async def breed(self, ctx, parent1: str, parent2: str):
        """Breeds two elements together to attempt an evolution fusion"""
        # Format the strings neatly to match keys
        p1 = parent1.replace("_", " ").title()
        p2 = parent2.replace("_", " ").title()

        # Validate inputs match existing species templates
        if p1 not in DRAGON_TEMPLATES or p2 not in DRAGON_TEMPLATES:
            await ctx.send("❌ Unknown dragon type! Use `!dex` to see valid parent species names. (Use quotes or spaces if multiple words, e.g., `!breed Fire_Drake Water_Serpent`) ")
            return

        await ctx.send(f"🧪 *The breeding ritual begins between your **{p1}** and **{p2}**...*")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.datetime.timedelta(seconds=2))

        # Genetic Math Logic
        parents = {p1, p2}
        child = None
        
        # Determine the resulting offspring variant based on elements combined
        if parents == {"Fire Drake", "Water Serpent"}:
            child = "Steam Leviathan"
        elif parents == {"Fire Drake", "Earth Wyrm"}:
            child = "Magma Behemoth"
        elif parents == {"Water Serpent", "Earth Wyrm"}:
            child = "Mud Hydra"
        elif p1 == p2 and DRAGON_TEMPLATES[p1]["tier"] == 2:
            # Breeding two identical Tier 2 hybrids gives a 15% chance for a Legendary Tier 3 Overlord
            if random.random() < 0.15:
                child = "Eclipse Overlord"
            else:
                child = p1 # Defaults back to matching the tier 2 parent
        else:
            # Standard baseline matching returns a common tier 1 variant randomly
            child = random.choice([p1, p2])

        info = DRAGON_TEMPLATES[child]
        
        # Highlight high tier legendary births
        color = 0x9b59b6 if info["tier"] == 3 else (0x2ecc71 if info["tier"] == 2 else 0x34495e)

        embed = discord.Embed(
            title="🥚 An Egg Has Hatched! 🥚",
            description=f"The ritual was a success! You have birthed a new **{child}**!",
            color=color
        )
        embed.add_field(name="Element", value=info["element"], inline=True)
        embed.add_field(name="Tier Class", value=f"⭐ Tier {info['tier']}", inline=True)
        embed.set_footer(text="Keep breeding higher tiers to discover cosmic entities!")
        
        await ctx.send(embed=embed)

    @breed.error
    async def breed_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Your incubator is cooling down! Wait **{int(error.retry_after)}s**.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing parameters! Correct layout format: `!breed [Parent1] [Parent2]`\nExample: `!breed Fire_Drake Water_Serpent` ")

async def setup(bot):
    await bot.add_cog(Dragons(bot))
