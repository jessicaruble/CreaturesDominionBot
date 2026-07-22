import discord
from discord.ext import commands
import sqlite3
import random
from db_manager import DB_PATH, get_profile

class Territory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helper function to initialize zones if they don't exist yet
    def init_zones(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        zones = ["Whispering Woods", "Obsidian Volcano", "Celestial Peaks"]
        for zone in zones:
            cursor.execute('INSERT OR IGNORE INTO territories (zone_name) VALUES (?)', (zone,))
        conn.commit()
        conn.close()

    # Prefix Command: !map or !territories
    @commands.command(name="map", aliases=["territories", "zones"])
    async def map_status(self, ctx):
        """Displays the tactical overview of all zones and who controls them"""
        self.init_zones() # Safely ensure default data maps exist

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT zone_name, controlling_faction, defense_score FROM territories')
        rows = cursor.fetchall()
        conn.close()

        embed = discord.Embed(
            title="🗺️ The Dominion Tactical Map",
            description="Factions fight for control over these strategic strongholds! Use `!attack [zone_number]` to conquer a region for your faction.",
            color=0x34495e
        )

        for i, row in enumerate(rows, start=1):
            name, faction, defense = row
            
            # Match layout emojis to faction identities
            f_emoji = "🛡️"
            if faction == "Human": f_emoji = "🔵"
            elif faction == "Dragon": f_emoji = "🟢"
            elif faction == "Creature Hunter": f_emoji = "🔴"

            embed.add_field(
                name=f"[{i}] {name}",
                value=f"**Controlled By:** {f_emoji} {faction}\n**Fortitude Defense:** {defense}/100 HP",
                inline=False
            )

        await ctx.send(embed=embed)

    # Prefix Command: !attack [Zone Number]
    @commands.command(name="attack", aliases=["siege", "conquer"])
    @commands.cooldown(1, 30, commands.BucketType.user) # 30-second siege battle fatigue
    async def attack(self, ctx, zone_id: str):
        """Launches a faction siege to damage a zone's defense system"""
        self.init_zones()

        # 1. Check if user belongs to a faction
        profile = get_profile(ctx.author.id)
        user_faction = profile["faction"] if profile else "None"

        if user_faction == "None":
            await ctx.send("❌ You are an independent traveler! Choose a side using `!setup_factions` before marching to war.")
            return

        # 2. Map indices to corresponding database strings
        zone_mapping = {"1": "Whispering Woods", "2": "Obsidian Volcano", "3": "Celestial Peaks"}
        if zone_id not in zone_mapping:
            await ctx.send("❌ Unknown theater of war! Choose a valid target index (1-3) from the map.")
            return

        target_zone = zone_mapping[zone_id]

        # 3. Pull target zone information out of storage
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT controlling_faction, defense_score FROM territories WHERE zone_name = ?', (target_zone,))
        controlling_faction, current_defense = cursor.fetchone()

        if controlling_faction == user_faction:
            await ctx.send(f"🏰 Your faction (**{user_faction}**) already controls **{target_zone}**! Fortify it by defending against rival raiders instead.")
            conn.close()
            return

        # 4. Siege Damage Calculation Mechanics
        damage = random.randint(15, 35)
        new_defense = current_defense - damage

        if new_defense <= 0:
            # Full Capture Event Triggered!
            cursor.execute('UPDATE territories SET controlling_faction = ?, defense_score = 100 WHERE zone_name = ?', (user_faction, target_zone))
            conn.commit()
            
            embed = discord.Embed(
                title="🚩 ZONE CAPTURED! 🚩",
                description=f"The defensive barricades of **{target_zone}** collapsed! {ctx.author.mention} led the charge and claimed the domain for the **{user_faction}** faction!",
                color=0x2ecc71
            )
        else:
            # Standard Structural Damage Event
            cursor.execute('UPDATE territories SET defense_score = ? WHERE zone_name = ?', (new_defense, target_zone))
            conn.commit()
            
            embed = discord.Embed(
                title="⚔️ Siege Infiltration Report",
                description=f"{ctx.author.mention} stormed **{target_zone}** representing the **{user_faction}** faction!",
                color=0xe74c3c
            )
            embed.add_field(name="Damage Inflicted", value=f"💥 **-{damage} Defense HP**", inline=True)
            embed.add_field(name="Remaining Fortitude", value=f"🛡️ **{new_defense}/100 HP**", inline=True)

        conn.close()
        await ctx.send(embed=embed)

    @attack.error
    async def attack_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Tactical fatigue! Your war units are regrouping. Retry in **{int(error.retry_after)}s**.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing parameters! Specify a target region number. Example: `!attack 1` ")

async def setup(bot):
    await bot.add_cog(Territory(bot))
