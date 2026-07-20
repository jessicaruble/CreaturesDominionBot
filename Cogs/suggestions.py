import discord
from discord.ext import commands

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prefix Command: !suggest [your suggestion text]
    @commands.command(name="suggest", aliases=["idea", "proposal"])
    @commands.cooldown(1, 60, commands.BucketType.user) # 1 suggestion per minute to prevent spam
    async def suggest(self, ctx, *, suggestion_text: str):
        """Submits a suggestion to the designated community suggestions channel"""
        # Always delete the user's raw text trigger message to keep channels clean
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        # Look for a specific channel named 'suggestions'. If missing, send it to the active channel.
        target_channel = discord.utils.get(ctx.guild.text_channels, name="suggestions") or ctx.channel

        embed = discord.Embed(
            title="💡 New Community Suggestion",
            description=suggestion_text,
            color=0x3498db
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text="Vote by reacting below! • Limit: 1 suggestion per min")

        # Send the suggestion embed
        suggestion_message = await target_channel.send(embed=embed)

        # Automatically add voting reactions
        await suggestion_message.add_reaction("👍")
        await suggestion_message.add_reaction("👎")

        # Confirm to the user privately if they sent it outside the suggestions channel
        if target_channel != ctx.channel:
            await ctx.send(f"✅ {ctx.author.mention}, your suggestion has been posted to {target_channel.mention}!", delete_after=5)

    # Handle cooldown errors gracefully
    @suggest.error
    async def suggest_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ You are suggesting too quickly! Please wait **{int(error.retry_after)}s** before submitting another idea.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please include your suggestion text! Example: `!suggest Add a trading system.` ", delete_after=5)

async def setup(bot):
    await bot.add_cog(Suggestions(bot))
