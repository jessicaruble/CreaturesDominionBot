import discord
from discord.ext import commands
from db_manager import create_profile, update_profile


class FactionButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    # Changed style from .blue to .blurple
    @discord.ui.button(label="Human Faction", style=discord.ButtonStyle.blurple, custom_id="faction_human")
    async def join_human(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_faction(interaction, "Human")

    # Changed style from .green to .success
    @discord.ui.button(label="Dragon Faction", style=discord.ButtonStyle.success, custom_id="faction_dragon")
    async def join_dragon(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_faction(interaction, "Dragon")

    # Changed style from .red to .danger
    @discord.ui.button(label="Creature Hunter", style=discord.ButtonStyle.danger, custom_id="faction_hunter")
    async def join_hunter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_faction(interaction, "Creature Hunter")

    async def handle_faction(self, interaction: discord.Interaction, faction_name: str):
        user = interaction.user
        guild = interaction.guild
        
        create_profile(user.id, guild.id)
        update_profile(user.id, "faction", faction_name)

        role = discord.utils.get(guild.roles, name=faction_name)
        if not role:
            role = await guild.create_role(name=faction_name, reason="Automated faction setup")

        faction_roles = ["Human", "Dragon", "Creature Hunter"]
        roles_to_remove = [discord.utils.get(guild.roles, name=r) for r in faction_roles if r != faction_name]
        for r in roles_to_remove:
            if r and r in user.roles:
                await user.remove_roles(r)

        await user.add_roles(role)
        await interaction.response.send_message(f"✨ You have successfully joined the **{faction_name}** faction!", ephemeral=True)

class Factions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup_factions")
    @commands.has_permissions(administrator=True)
    async def setup_factions(self, ctx):
        embed = discord.Embed(
            title="⚔️ Choose Your Faction ⚔️",
            description="Select your path in the Creatures Dominion! Clicking a button saves your progress to your profile and gives you access to faction channels.",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed, view=FactionButtons())

async def setup(bot):
    await bot.add_cog(Factions(bot))
