import discord
from discord.ext import commands
import random
import sqlite3
import asyncio
from db_manager import DB_PATH, create_profile

TRIVIA_QUESTIONS = [
    {
        "q": "What type of dragon element is birthed by breeding a Fire Drake and a Water Serpent?",
        "a": "steam leviathan"
    },
    {
        "q": "Which faction is colored RED on our tactical selection board?",
        "a": "creature hunter"
    },
    {
        "q": "What is the maximum evolutionary class/tier level currently available in the Dominion database?",
        "a": "3"
    }
]

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- UPDATED COMMAND: !help ---
    @commands.command(name="help", aliases=["commands", "menu"])
    async def help_menu(self, ctx):
        """Displays a clean navigation directory of all active bot features"""
        embed = discord.Embed(
            title="⚔️ Creatures Dominion Command Directory ⚔️",
            description="Welcome ranger! Here is the complete list of system inputs available to guide your journey.",
            color=0x34495e
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.add_field(
            name="🎮 Core RPG Actions", 
            value="`!profile` - View stats, level progress, and active equipment.\n"
                  "`!spawn` - Summon a random wild beast or dragon encounter.\n"
                  "`!bond` - Attempt a soul alignment match with active spawns.\n"
                  "`!dragon_index` - View the entire dragon genetic evolution pool.\n"
                  "`!breed [p1] [p2]` - Fuse two dragons together to roll for a rare hybrid.",
            inline=False
        )
        embed.add_field(
            name="💰 Economy & Marketplace", 
            value="`!balance` - View your total gold coins held in vaults.\n"
                  "`!daily` - Claim your 24-hour gold allowance allowance.\n"
                  "`!shop` - Open the trading post catalog to purchase weapons.\n"
                  "`!buy [item]` - Order an item and equip it directly to your bag.\n"
                  "`!inventory` - Peek inside your adventure knapsack pack.", 
            inline=False
        )
        embed.add_field(
            name="📈 Rankings & Factions", 
            value="`!leaderboard` - View the top 10 highest-level active players.\n"
                  "`!richest` - View the wealthiest coin tycoons across the sectors.\n"
                  "`!map` - Inspect global territory holdings and faction lines.\n"
                  "`!attack [zone]` - Launch a siege strike for your faction.", 
            inline=False
        )
        embed.add_field(
            name="💡 Community Support & Mini-Games", 
            value="`!suggest [text]` - Submit an idea with an automated voting poll.\n"
                  "`!bug [text]` - File an error trace log directly to staff rooms.\n"
                  "`!trivia` - Launch a fast chat quiz challenge to earn 100 gold.\n"
                  "`!coinflip [side] [bet]` - Gamble your coins on a coin flip.", 
            inline=False
        )
        embed.add_field(
            name="🛡️ Staff Controls & Broadcasts", 
            value="`!setup_verify` / `!setup_factions` / `!setup_tickets` - Spawn interactive buttons.\n"
                  "`!setup_roles` - Automatically synthesize missing server roles.\n"
                  "`!announce [hex] [Title] | [Message]` - Cast clean embeds.\n"
                  "`!prof_announce [Title] | [Topic] | [Body]` - Broadcast executive-style posts.\n"
                  "`!warn / !warnings / !purge / !kick / !ban` - Moderation tools.", 
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {ctx.author.name} • Prefix: !")
        await ctx.send(embed=embed)

    @commands.command(name="trivia", aliases=["quiz", "game"])
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def trivia(self, ctx):
        challenge = random.choice(TRIVIA_QUESTIONS)
        embed = discord.Embed(
            title="🧠 Dominion Trivia Challenge!",
            description=f"**Question:**\n{challenge['q']}\n\n*Type your answer directly in the chat below! You have 15 seconds.*",
            color=0x3498db
        )
        embed.set_footer(text="Reward: 💰 100 Gold Coins!")
        await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel and m.content.lower().strip() == challenge['a']

        try:
            winner_msg = await self.bot.wait_for('message', check=check, timeout=15.0)
            create_profile(winner_msg.author.id, ctx.guild.id)
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('UPDATE profiles SET coins = coins + 100 WHERE user_id = ?', (winner_msg.author.id,))
            conn.commit()
            conn.close()

            success_embed = discord.Embed(
                title="🏆 Trivia Winner!",
                description=f"Congratulations {winner_msg.author.mention}! Your answer was correct.\n**Answer:** {challenge['a'].title()}\n\n💰 **+100 Gold Coins** has been added to your profile vault!",
                color=0x2ecc71
            )
            await ctx.send(embed=success_embed)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ Trivia Time Expired!",
                description=f"No one guessed the correct answer in time!\n\n**Correct Answer was:** `{challenge['a'].title()}`",
                color=0xe74c3c
            )
            await ctx.send(embed=timeout_embed)

    @commands.command(name="coinflip", aliases=["flip", "bet"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def coinflip(self, ctx, side: str, bet: int):
        create_profile(ctx.author.id, ctx.guild.id)
        chosen_side = side.lower().strip()

        if chosen_side not in ["heads", "tails"]:
            await ctx.send("❌ Invalid choice! Choose either `heads` or `tails`.\nExample: `!coinflip heads 50`")
            return
        if bet <= 0:
            await ctx.send("❌ Your wager amount must be greater than 0 gold coins!")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT coins FROM profiles WHERE user_id = ?', (ctx.author.id,))
        current_coins = cursor.fetchone()

        if current_coins < bet:
            await ctx.send(f"❌ Transaction declined! You only have **💰 {current_coins}** coins in your vault.")
            conn.close()
            return

        outcome = random.choice(["heads", "tails"])
        await ctx.send(f"🪙 *The gold coin spins into the air...*")
        await asyncio.sleep(1.5)

        if chosen_side == outcome:
            cursor.execute('UPDATE profiles SET coins = coins + ? WHERE user_id = ?', (bet, ctx.author.id))
            conn.commit()
            embed = discord.Embed(
                title="💰 YOU WIN! 💰",
                description=f"The coin landed on **{outcome.upper()}**!\n\nYour bet was successful. You earned **💰 +{bet}** coins!",
                color=0x2ecc71
            )
        else:
            cursor.execute('UPDATE profiles SET coins = coins - ? WHERE user_id = ?', (bet, ctx.author.id))
            conn.commit()
            embed = discord.Embed(
                title="📉 YOU LOSE",
                description=f"The coin landed on **{outcome.upper()}**!\n\nYou guessed incorrectly and lost **💰 -{bet}** coins.",
                color=0xe74c3c
            )
        conn.close()
        await ctx.send(embed=embed)

    @coinflip.error
    @trivia.error
    async def fun_errors(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Game cooling down! Wait **{int(error.retry_after)}s**.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Parameter missing! Correct template syntax format:\n`!coinflip [heads/tails] [amount]`")

async def setup(bot):
    await bot.add_cog(Fun(bot))
