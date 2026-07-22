import discord
from discord.ext import commands
import sqlite3
from db_manager import DB_PATH, create_profile, add_item_to_inventory


SHOP_INVENTORY = {
    "sword": {"name": "⚔️ Hunter's Steel Sword", "price": 200, "desc": "Increases quest success rates slightly."},
    "shield": {"name": "🛡️ Aegis Guardian Shield", "price": 350, "desc": "Fortifies your territory defense stats."},
    "potion": {"name": "🧪 Mystic Breeding Elixir", "price": 500, "desc": "Boosts chances of Tier 3 fusions by 10%."},
    "egg": {"name": "🥚 Unstable Dragon Egg", "price": 1000, "desc": "Hatch immediately to roll for a rare species."}
}

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_coins(self, user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT coins FROM profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0

    def update_coins(self, user_id, amount):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE profiles SET coins = coins + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()

    @commands.command(name="balance", aliases=["bal", "coins"])
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        create_profile(member.id, ctx.guild.id)
        coins = self.get_coins(member.id)
        
        embed = discord.Embed(
            title=f"💰 {member.display_name}'s Vault",
            description=f"You currently possess **{coins}** gold coins in the dominion.",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="daily")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        create_profile(ctx.author.id, ctx.guild.id)
        reward = 250
        self.update_coins(ctx.author.id, reward)
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You gathered your daily allowance and found **{reward}** gold coins!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            hours = int(error.retry_after // 3600)
            minutes = int((error.retry_after % 3600) // 60)
            await ctx.send(f"⏳ Your daily reward is still recharging! Try again in **{hours}h {minutes}m**.")
        else:
            raise error

    @commands.command(name="richest", aliases=["baltop", "moneytop"])
    async def richest(self, ctx):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, coins FROM profiles ORDER BY coins DESC LIMIT 10')
        top_wealthy = cursor.fetchall()
        conn.close()

        if not top_wealthy:
            await ctx.send("❌ No economic records found inside the Dominion archives!")
            return

        embed = discord.Embed(
            title="💰 Creatures Dominion Wealthiest Tycoons 💰",
            description="The most financially prosperous rangers hoarding gold across server sectors.",
            color=0xf1c40f
        )
        leaderboard_string = ""
        for rank_num, (user_id, coins) in enumerate(top_wealthy, start=1):
            member = ctx.guild.get_member(user_id)
            name_str = member.mention if member else f"Hidden Trader (ID: {user_id})"
            medal = "🔹"
            if rank_num == 1: medal = "👑"
            elif rank_num == 2: medal = "💎"
            elif rank_num == 3: medal = "💰"
            leaderboard_string += f"{medal} **#{rank_num}** | {name_str} — **💰 {coins}** coins\n"

        embed.description = f"{embed.description}\n\n{leaderboard_string}"
        await ctx.send(embed=embed)

    @commands.command(name="shop", aliases=["market", "store"])
    async def shop(self, ctx):
        embed = discord.Embed(
            title="🛒 The Dominion Black Market",
            description="Exchange your gold coins for gear and breeding modifications! Use `!buy [item_id]` to purchase an item.",
            color=0xe74c3c
        )
        for item_id, item_info in SHOP_INVENTORY.items():
            embed.add_field(
                name=f"{item_info['name']} (`{item_id}`)",
                value=f"**Price:** 💰 {item_info['price']} gold\n*{item_info['desc']}*",
                inline=False
            )
        embed.set_footer(text=f"Your current balance: 💰 {self.get_coins(ctx.author.id)} gold")
        await ctx.send(embed=embed)

    @commands.command(name="buy", aliases=["purchase"])
    async def buy(self, ctx, item_id: str):
        create_profile(ctx.author.id, ctx.guild.id)
        target_id = item_id.lower().strip()

        if target_id not in SHOP_INVENTORY:
            await ctx.send("❌ Item not found! Look at the `!shop` catalog menu to view valid keywords.")
            return

        item = SHOP_INVENTORY[target_id]
        player_balance = self.get_coins(ctx.author.id)

        if player_balance < item["price"]:
            await ctx.send(f"❌ Purchase denied! You need **💰 {item['price']}** coins, but you only possess **💰 {player_balance}**.")
            return

        # Deduct transaction value directly and save the physical item to their inventory
        self.update_coins(ctx.author.id, -item["price"])
        add_item_to_inventory(ctx.author.id, item["name"])

        embed = discord.Embed(
            title="📦 Purchase Receipt Confirmed!",
            description=f"You successfully imported equipment out of the market bazaar storage arrays.",
            color=0x2ecc71
        )
        embed.add_field(name="Acquired Item", value=item["name"], inline=True)
        embed.add_field(name="Price Charged", value=f"💰 **-{item['price']} Gold**", inline=True)
        embed.set_footer(text="Type !inventory to view all your owned bags and gear!")
        
        await ctx.send(content=ctx.author.mention, embed=embed)

    # --- NEW PREFIX COMMAND: !inventory ---
    @commands.command(name="inventory", aliases=["inv", "bag"])
    async def inventory(self, ctx, member: discord.Member = None):
        """Displays a clean catalog sheet tracking all items owned by a user"""
        member = member or ctx.author
        user_items = get_user_inventory(member.id)

        embed = discord.Embed(
            title=f"🎒 {member.display_name}'s Adventure Bag",
            color=0x34495e
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        if not user_items:
            embed.description = "This inventory knapsack is completely empty! Go purchase tools using `!shop`."
        else:
            inv_string = ""
            for item_name, qty in user_items:
                inv_string += f"🔹 **{item_name}** x{qty}\n"
            embed.description = inv_string

        await ctx.send(embed=embed)

    @buy.error
    async def buy_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing parameters! Specify an item ID string. Example: `!buy sword` ")

async def setup(bot):
    await bot.add_cog(Economy(bot))
