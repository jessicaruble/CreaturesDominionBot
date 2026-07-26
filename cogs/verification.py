import discord
from discord.ext import commands


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="verify",
        description="Verify yourself and get the Verified role"
    )
    async def verify(self, interaction: discord.Interaction):

        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        role = discord.utils.get(
            interaction.guild.roles,
            name="Verified"
        )

        if role is None:
            await interaction.response.send_message(
                "❌ The Verified role was not found. Create a role named exactly: Verified",
                ephemeral=True
            )
            return

        if role in interaction.user.roles:
            await interaction.response.send_message(
                "✅ You are already verified!",
                ephemeral=True
            )
            return

        try:
            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                "✅ Verification complete! You now have access.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I cannot give you the role. Move my bot role above Verified and enable Manage Roles.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Verification(bot))
