import discord
from discord.ext import commands
import sqlite3
import random
from  db_manager import DB_PATH, create_profile

# Define the level rank role unlocks and their custom colors
LEVEL_ROLES = {
    5: {"name": "Novice Tamer", "color": 0x3498db},      # Cyan Blue
    10: {"name": "Elite Hunter", "color": 0xe67e22},    # Orange
    20: {"name": "Dominion Overlord", "color": 0x9b59b6} # Purple
}

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith('!'):
            return

        user_id = message.author.id
        guild_id = message.guild.id

        current_time = message.created_at.timestamp()
        if user_id in self.cooldowns:
            if current_time - self.cooldowns[user_id] < 60:
                return 

        self.cooldowns[user_id] = current_time
        create_profile(user_id, guild_id)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level FROM profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()

        if row:
            current_xp, current_level = row
            xp_to_add = random.randint(15, 25)
            new_xp = current_xp + xp_to_add
            xp_needed = current_level * 100

            if new_xp >= xp_needed:
                new_level = current_level + 1
                new_xp = new_xp - xp_needed 
                
                cursor.execute('UPDATE profiles SET xp = ?, level = ? WHERE user_id = ?', (new_xp, new_level, user_id))
                conn.commit()
                
                role_reward_text = ""
                
                if new_level in LEVEL_ROLES:
                    role_info = LEVEL_ROLES[new_level]
                    guild = message.guild
                    
                    role = discord.utils.get(guild.roles, name=role_info["name"])
                    if not role:
                        try:
                            role = await guild.create_role(
                                name=role_info["name"],
                                color=discord.Color(role_info["color"]),
                                reason=f"Automated level rank reward for Level {new_level}"
                            )
                        except discord.Forbidden:
                            role = None
                    
                    if role:
                        try:
                            await message.author.add_roles(role)
                            role_reward_text = f"\n\n🏆 **RANK UNLOCK:** You have been awarded the **{role.name}** role!"
                        except discord.Forbidden:
                            role_reward_text = f"\n\n⚠️ *Could not assign rank role. Make sure the bot's role is dragged to the top of the Server Roles list!*"

                embed = discord.Embed(
                    title="🎉 LEVEL UP! 🎉",
                    description=f"Congratulations {message.author.mention}! Your training paid off.\n"
                                f"You have ascended to **Level {new_level}** in the Dominion!{role_reward_text}",
                    color=0x3498db
                )
                await message.channel.send(embed=embed)
            else:
                cursor.execute('UPDATE profiles SET xp = ? WHERE user_id = ?', (new_xp, user_id))
                conn.commit()
        
        conn.close()

    @commands.command(name="rank", aliases=["lvl", "level"])
    async def rank(self, ctx, member: discord.Member = None):
        """Displays a clean status breakdown card of current XP levels"""
        member = member or ctx.author
        create_profile(member.id, ctx.guild.id)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level FROM profiles WHERE user_id = ?', (member.id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            xp, level = row
            xp_needed = level * 100
            
            embed = discord.Embed(
                title=f"📈 {member.display_name}'s Progression",
                color=0xe67e22
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Current Level", value=f"⭐ **Level {level}**", inline=True)
            embed.add_field(name="Experience Progress", value=f"🔷 **{xp} / {xp_needed} XP**", inline=True)
            
            progress = int((xp / xp_needed) * 10)
            bar = "🟩" * progress + "⬛" * (10 - progress)
            embed.add_field(name="Progress Bar", value=bar, inline=False)
            
            next_milestones = [m for m in LEVEL_ROLES.keys() if m > level]
            if next_milestones:
                next_lvl = min(next_milestones)
                embed.set_footer(text=f"Next Rank Reward: '{LEVEL_ROLES[next_lvl]['name']}' at Level {next_lvl}")
            else:
                embed.set_footer(text="You have unlocked all current level rank rewards!")

            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Could not load progression statistics profile.")

    # --- NEW PREFIX COMMAND: !leaderboard ---
    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        """Fetches the top 10 highest-ranking players across the Dominion database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Query the database sorting first by level, then by residual XP totals
        cursor.execute('''
            SELECT user_id, level, xp 
            FROM profiles 
            ORDER BY level DESC, xp DESC 
            LIMIT 10
        ''')
        top_players = cursor.fetchall()
        conn.close()

        if not top_players:
            await ctx.send("❌ No data available in the Dominion records yet!")
            return

        embed = discord.Embed(
            title="⚔️ Creatures Dominion Hall of Fame ⚔️",
            description="The most powerful and active rangers inside our dominion server sectors.",
            color=0xf1c40f # Gold theme color
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        leaderboard_string = ""
        
        # Loop through data and format entries into a visually appealing ranking list
        for rank_num, (user_id, level, xp) in enumerate(top_players, start=1):
            # Try to get the user from cache or fetch from discord API safely if cached out
            member = ctx.guild.get_member(user_id)
            name_str = member.mention if member else f"Unknown Ranger (ID: {user_id})"
            
            # Choose a trophy emoji based on rank
            medal = "🔹"
            if rank_num == 1: medal = "🥇"
            elif rank_num == 2: medal = "🥈"
            elif rank_num == 3: medal = "🥉"

            leaderboard_string += f"{medal} **#{rank_num}** | {name_str} — **Lvl {level}** *(XP: {xp})*\n"

        embed.description = f"{embed.description}\n\n{leaderboard_string}"
        embed.set_footer(text=f"Requested by {ctx.author.name} • Updates instantly")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
