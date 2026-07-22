
import discord
from discord.ext import commands

class ServerLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Replace this with the exact name of the text channel where logs should be sent
        self.LOG_CHANNEL_NAME = "server-logs"

    def get_log_channel(self, guild):
        """Helper function to safely find the logging channel by name."""
        return discord.utils.get(guild.text_channels, name=self.LOG_CHANNEL_NAME)

    # 1. Track Deleted Messages
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return  # Ignore bots

        channel = self.get_log_channel(message.guild)
        if not channel:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"A message sent by {message.author.mention} was deleted in {message.channel.mention}.",
            color=discord.Color.red()
        )
        # Handle empty/image-only content safely
        content = message.content if message.content else "*[No text content (likely an attachment)]*"
        embed.add_field(name="Content:", value=content, inline=False)
        embed.set_footer(text=f"User ID: {message.author.id}")
        await channel.send(embed=embed)

    # 2. Track Edited Messages
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return  # Ignore bots or edits that didn't change text (like link previews)

        channel = before.guild if before.guild else None
        if not channel:
            return
            
        log_channel = self.get_log_channel(before.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="✏️ Message Edited",
            description=f"A message by {before.author.mention} was edited in {before.channel.mention}.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Before:", value=before.content or "*[Empty]*", inline=False)
        embed.add_field(name="After:", value=after.content or "*[Empty]*", inline=False)
        embed.set_footer(text=f"User ID: {before.author.id}")
        await log_channel.send(embed=embed)

    # 3. Track Member Joins
    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = self.get_log_channel(member.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} ({member.name}) has joined the server.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account Created:", value=member.created_at.strftime("%B %d, %Y"), inline=False)
        embed.set_footer(text=f"User ID: {member.id}")
        await log_channel.send(embed=embed)

    # 4. Track Member Leaves
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = self.get_log_channel(member.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="📤 Member Left",
            description=f"{member.mention} ({member.name}) has left the server.",
            color=discord.Color.dark_grey()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"User ID: {member.id}")
        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerLogs(bot))
    print("✅ Logging system initialized successfully!")
