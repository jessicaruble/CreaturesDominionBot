import discord
from discord.ext import commands
import random
import sqlite3
import asyncio
from database.db_manager import DB_PATH, create_profile

# Main Expedition Mission Matrix
QUEST_MISSIONS = {
    "1": {
        "name": "🌲 Scout the Whispering Woods",
        "difficulty": "Easy",
        "time": 5, # Seconds for fast mobile testing
        "success_rate": 0.90,
        "reward_coins": 50,
        "reward_xp": 20
    },
    "2": {
        "name": "⚔️ Raid a Creature Hunter Outpost",
        "difficulty": "Medium",
        "time": 10,
        "success_rate": 0.70,
        "reward_coins": 150,
        "reward_xp": 50
    },
    "3": {
        "name": "🌋 Explore the Obsidian Core",
        "difficulty": "Hard",
        "time": 15,
        "success_rate": 0.45,
        "reward_coins": 400,
        "reward_xp": 120
    }
}

class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Local memory set to track who is currently away on a quest
        self.active_questers = set()

    # Prefix Command: !quests
    @commands.command(name="quests", aliases=["questlist", "missions"])
    async def quests(self, ctx):
        """Displays all available active missions in the Dominion"""
        embed = discord.Embed(
            title="📜 The Dominion Quest Board",
            description="Send your characters out to secure territory and harvest treasure! Type `!adventure [number]` to launch.",
            color=0x34495e
        )
        
        for q_id, q_info in QUEST_MISSIONS.items():
            embed.add_field(
                name=f"[{q_id}] {q_info['name']}",
                value=f"**Difficulty:** {q_info['difficulty']}\n"
                      f"**Duration:** {q_info['time']}s\n"
                      f"**Rewards:** 💰 {q_info['reward_coins']} | 🔷 {q_info['reward_xp']} XP",
                inline=False
            )
            
        await ctx.send(embed=embed)

    # Prefix Command: !adventure [Quest ID]
    @commands.command(name="adventure", aliases=["startquest", "runmission"])
    async def adventure(self, ctx, quest_id: str):
        """Dispatches the user on a specific time-delayed text expedition"""
        if ctx.author.id in self.active_questers:
            await ctx.send("❌ You are already out exploring the wilderness! Finish your active journey first.")
            return

        if quest_id not in QUEST_MISSIONS:
            await ctx.send("❌ Invalid assignment! Use `!quests` to choose a mission number between 1 and 3.")
            return

        mission = QUEST_MISSIONS[quest_id]
        self.active_questers.add(ctx.author.id)
        create_profile(ctx.author.id, ctx.guild.id)

        await ctx.send(f"🚀 {ctx.author.mention} has left the safety of the base camps to pursue **{mission['name']}**! Traveling time: **{mission['time']} seconds**...")

        # Asynchronously wait for the duration of the quest without locking up the rest of the bot
        await asyncio.sleep(mission['time'])

        # Quest Completion Calculations
        roll = random.random()
        
        if roll <= mission['success_rate']:
            # Success: Open Database and award prizes
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Add Gold Coins
            cursor.execute('UPDATE profiles SET coins = coins + ? WHERE user_id = ?', (mission['reward_coins'], ctx.author.id))
            
            # Fetch current level variables to calculate XP progression cleanly
            cursor.execute('SELECT xp, level FROM profiles WHERE user_id = ?', (ctx.author.id,))
            current_xp, current_level = cursor.fetchone()
            
            new_xp = current_xp + mission['reward_xp']
            xp_needed = current_level * 100
            
            level_up_occurred = False
            if new_xp >= xp_needed:
                current_level += 1
                new_xp = new_xp - xp_needed
                level_up_occurred = True
                cursor.execute('UPDATE profiles SET level = ? WHERE user_id = ?', (current_level, ctx.author.id))

            cursor.execute('UPDATE profiles SET xp = ? WHERE user_id = ?', (new_xp, ctx.author.id))
            conn.commit()
            conn.close()

            embed = discord.Embed(
                title="🏆 Quest Victorious! 🏆",
                description=f"Welcome back, {ctx.author.mention}! Your tactics were flawless.",
                color=0x2ecc71
            )
            embed.add_field(name="Loot Extracted", value=f"💰 **+{mission['reward_coins']} Gold Coins**", inline=True)
            embed.add_field(name="Training Gained", value=f"🔷 **+{mission['reward_xp']} Experience Points**", inline=True)
            
            if level_up_occurred:
                embed.add_field(name="✨ Level Up Announcement ✨", value=f"You ascended to **Level {current_level}**!", inline=False)
                
            await ctx.send(content=ctx.author.mention, embed=embed)
        else:
            # Failure state outcome
            embed = discord.Embed(
                title="💀 Mission Failed! 💀",
                description=f"Disaster struck during the quest line, {ctx.author.mention}! Your squadron was ambushed and forced to retreat with empty pockets.",
                color=0xe74c3c
            )
            await ctx.send(content=ctx.author.mention, embed=embed)

        # Remove the lock flag so they can go out on adventures again
        self.active_questers.remove(ctx.author.id)

    @adventure.error
    async def adventure_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing parameters! Specify a quest digit. Example: `!adventure 1` ")

async def setup(bot):
    await bot.add_cog(Quests(bot))
