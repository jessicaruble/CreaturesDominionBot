import discord
from discord.ext import commands

# Complete role blueprint layout map for your server
ROLE_BLUEPRINT = {
    # 1. Staff & Administration Roles
    "Staff": 0x2ecc71,       # Emerald Green
    "Moderator": 0x3498db,   # Cyan Blue
    "Alpha Tester": 0xe74c3c, # Crimson Red

    # 2. Base Security
    "Verified": 0x95a5a6,    # Silver Gray

    # 3. Game Factions
    "Human": 0x34495e,       # Dark Slate Blue
    "Dragon": 0x2ecc71,      # Lime Green
    "Creature Hunter": 0x9b59b6, # Dark Purple

    # 4. Special Achievement Badge Roles
    "Elite Breeder": 0xf1c40f,   # Gold
    "Dominion Conqueror": 0xe67e22, # Orange
    "Legendary Tamer": 0xff007f   # Neon Pink
}

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Admin Prefix Command: !setup_roles
    @commands.command(name="setup_roles", aliases=["createroles", "syncroles"])
    @commands.has_permissions(administrator=True)
    async def setup_roles(self, ctx):
        """Scans the server and automatically creates any missing game/staff roles"""
        await ctx.send("⚙️ *Analyzing server data and generating your Dominion role blueprints...*")
        
        guild = ctx.guild
        created_count = 0
        skipped_count = 0

        # Loop through our blueprint matrix
        for role_name, color_hex in ROLE_BLUEPRINT.items():
            # Check if the role already exists to prevent duplicates
            existing_role = discord.utils.get(guild.roles, name=role_name)
            
            if not existing_role:
                try:
                    # Create the role with its custom gaming color
                    await guild.create_role(
                        name=role_name,
                        color=discord.Color(color_hex),
                        reason="Automated game layout role initialization."
                    )
                    created_count += 1
                except discord.Forbidden:
                    await ctx.send("❌ Error: The bot lacks 'Manage Roles' permissions to create roles!")
                    return
            else:
                skipped_count += 1

        # Summary completion report
        embed = discord.Embed(
            title="🎭 Role Synchronization Complete",
            description=f"Your server roles are perfectly aligned with the Creatures Dominion system database!",
            color=0x2ecc71
        )
        embed.add_field(name="✨ Roles Created", value=f"**{created_count}** new roles built.", inline=True)
        embed.add_field(name="⏭️ Roles Skipped", value=f"**{skipped_count}** already existed.", inline=True)
        embed.set_footer(text="Staff Tip: Remember to drag the Bot's role to the top of the Discord role hierarchy list!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Roles(bot))
