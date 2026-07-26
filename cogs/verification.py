import discord
from discord.ext import commands

class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Verify Here", style=discord.ButtonStyle.success, custom_id="verify_member")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Look for or create a "Verified" role
        role = discord.utils.get(guild.roles, name="Verified")
        if not role:
            role = await guild.create_role(name="Verified", reason="Automated verification setup")

        if role in user.roles:
            await interaction.response.send_message("❌ You are already verified!", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message("🎉 Access granted! Welcome to the server.", ephemeral=True)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup_verify")
    @commands.has_permissions(administrator=True)
    async def setup_verify(self, ctx):
        embed = discord.Embed(
            title="🔒 Security Verification",
            description="Welcome to the server! Click the button below to verify your account and view the channels.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=VerifyButton())

async def setup(bot):
    await bot.add_cog(Verification(bot))
