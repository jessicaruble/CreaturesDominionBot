import discord
from discord.ext import commands
import random

class Bugs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prefix Command: !bug [details of the bug]
    @commands.command(name="bug", aliases=["reportbug", "glitch"])
    @commands.cooldown(1, 30, commands.BucketType.user) # 30-second cooldown per user
    async def bug(self, ctx, *, bug_report: str):
        """Submits a glitch/bug tracking report directly to the staff review room"""
        # Delete the trigger text command to keep user channels tidy
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        # Generate a random 4-digit tracking number (e.g., #4821)
        case_id = random.randint(1000, 9999)

        # Look for a secure channel named 'bug-reports' or 'staff-logs'
        staff_channel = discord.utils.get(ctx.guild.text_channels, name="bug-reports") or \
                        discord.utils.get(ctx.guild.text_channels, name="staff-logs") or \
                        ctx.channel # Fallback to current channel if channel is missing

        embed = discord.Embed(
            title=f"🐛 Bug Report Filed — Case #{case_id}",
            description=bug_report,
            color=0xe74c3c # High-alert red
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Reporter ID: {ctx.author.id} • Status: Pending Review")

        # Send to the staff channel layout
        await staff_channel.send(embed=embed)

        # Send a brief temporary DM or notice confirming submission success
        await ctx.send(f"✅ Thank you {ctx.author.mention}! Your report has been logged as **Case #{case_id}** and sent to the development team.", delete_after=5)

    # Cooldown error processing handler
    @bug.error
    async def bug_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Please wait **{int(error.retry_after)}s** before reporting another bug.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please describe the bug! Example: `!bug The !daily command didn't give me coins.`", delete_after=5)

async def setup(bot):
    await bot.add_cog(Bugs(bot))
