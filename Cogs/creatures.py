import discord
from discord.ext import commands
import random
import sqlite3
from database.db_manager import DB_PATH, create_profile

CREATURE_DATA = {
    "Infernal Drake": {
        "type": "Dragon",
        "rarity": "Rare",
        "description": "A fierce dragon born in volcanic fissures. Its scales burn like embers."
    },
    "Frost Wyrm": {
        "type": "Dragon",
        "rarity": "Epic",
        "description": "An ancient, frozen leviathan whose breath freezes time and oceans."
    },
    "Forest Spriggan": {
        "type": "Creature",
        "rarity": "Common",
        "description": "A woodland spirit made of roots and moss. Quiet, unless its grove is harmed."
    },
    "Shadow Stalker": {
        "type": "Beast",
        "rarity": "Uncommon",
        "description": "A feline predator that hunts entirely within the shadows of mountains."
    },
    "Celestial Phoenix": {
        "type": "Mythic",
        "rarity": "Legendary",
        "description": "A rare cosmic bird that collapses into a star when it passes away, only to be reborn."
    }
}

class Creatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spawn")
    async def spawn(self, ctx):
        name, info = random.choice(list(CREATURE_DATA.items()))
        embed = discord.Embed(
            title=f"⚠️ A Wild {name} Appears!",
            description=f"**Type:** {info['type']} | **Rarity:** {info['rarity']}\n\n*{info['description']}*",
            color=0xe74c3c
        )
        embed.set_footer(text="Type !bond to attempt to bind this creature to your soul!")
        self.bot.last_spawned = name
        await ctx.send(embed=embed)

    @commands.command(name="bond")
    async def bond(self, ctx):
        if not hasattr(self.bot, 'last_spawned') or self.bot.last_spawned is None:
            await ctx.send("❌ There are no wild creatures nearby to bond with right now! Use `!spawn` first.")
            return

        create_profile(ctx.author.id, ctx.guild.id)
        creature_name = self.bot.last_spawned
        success = random.choice([True, False])
        
        if success:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('UPDATE profiles SET bonded_creature = ? WHERE user_id = ?', (creature_name, ctx.author.id))
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✨ Soul Bond Formed! ✨",
                description=f"You successfully bonded with the **{creature_name}**!",
                color=0x2ecc71
            )
            self.bot.last_spawned = None
        else:
            embed = discord.Embed(
                title="💨 The Creature Escaped!",
                description=f"The **{creature_name}** vanished into the wild.",
                color=0x95a5a6
            )
        await ctx.send(embed=embed)

    # --- UPDATED PROFILE WITH INVENTORY BUILT IN ---
    @commands.command(name="profile", aliases=["p"])
    async def profile(self, ctx, member: discord.Member = None):
        """Displays full game metadata details for a player profile with inventory"""
        member = member or ctx.author
        create_profile(member.id, ctx.guild.id)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT coins, xp, level, faction, bonded_creature FROM profiles WHERE user_id = ?', (member.id,))
        row = cursor.fetchone()
        
        # Fetch inventory rows safely
        cursor.execute('SELECT item_name, quantity FROM inventory WHERE user_id = ?', (member.id,))
        inv_rows = cursor.fetchall()
        conn.close()
        
        if row:
            coins, xp, level, faction, bonded = row
            embed = discord.Embed(
                title=f"👤 {member.display_name}'s Dominion Profile",
                color=0x34495e
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="📊 Statistics", value=f"**Level:** {level}\n**XP:** {xp}\n**Coins:** 💰 {coins}", inline=True)
            embed.add_field(name="⚔️ Affiliations", value=f"**Faction:** {faction}\n**Bonded Beast:** {bonded}", inline=True)
            
            if not inv_rows:
                inv_text = "No tools equipped."
            else:
                inv_text = ", ".join([f"{name} (x{qty})" for name, qty in inv_rows])
                
            embed.add_field(name="🎒 Gear & Equipment", value=inv_text, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Error loading your player profile.")

async def setup(bot):
    await bot.add_cog(Creatures(bot))
