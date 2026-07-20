import discord
from discord.ext import commands
import datetime

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Admin Prefix Command: !announce
    @commands.command(name="announce", aliases=["embed", "broadcast"])
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx, color_hex: str, *, content_text: str):
        """Creates and broadcasts a highly customized rich announcement embed panel"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        if "|" not in content_text:
            await ctx.send("❌ Incorrect format! Please split your title and message using a pipe `|` character.\nExample: `!announce #ff5500 Patch Notes | Added a brand new dragon element!`", delete_after=10)
            return

        title, description = content_text.split("|", 1)

        try:
            color_value = int(color_hex.lstrip("#"), 16)
        except ValueError:
            color_value = 0x34495e

        embed = discord.Embed(
            title=title.strip(),
            description=description.strip(),
            color=color_value
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"Broadcasted by {ctx.author.display_name} • Creatures Dominion Dev Team")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

        await ctx.send(embed=embed)

    # --- NEW PROFESSIONAL ANNOUNCEMENT ENGINE ---
    @commands.command(name="prof_announce", aliases=["pa", "official"])
    @commands.has_permissions(administrator=True)
    async def prof_announce(self, ctx, *, content_text: str):
        """Broadcasts a professional executive-style network announcement panel"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        # Split using structural pipes: Title | Subtitle | Message Content
        if content_text.count("|") < 2:
            await ctx.send("❌ Format Error! Use two pipes split like this:\n`!prof_announce Title | Subtitle / Topic | Detailed message description body` ", delete_after=12)
            return

        parts = content_text.split("|", 2)
        title = parts[0].strip()
        subtitle = parts[1].strip()
        body_text = parts[2].strip()

        # Professional Slate Blue Hex configuration
        corporate_blue = 0x2b465e 

        embed = discord.Embed(
            title=f"📢 {title.upper()}",
            description=f"**📋 Topic:** {subtitle}\n"
                        f"**📅 Date:** {datetime.datetime.now().strftime('%B %d, %Y')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"{body_text}",
            color=corporate_blue
        )
        
        # Formatting structural anchors
        if ctx.guild.icon:
            embed.set_author(name=f"{ctx.guild.name} Official Network Bulletin", icon_url=ctx.guild.icon.url)
        else:
            embed.set_author(name="Creatures Dominion Executive Broadcast")
            
        embed.set_footer(text=f"Authorized By: {ctx.author.display_name} | Security Status: Verified ✅")

        await ctx.send(embed=embed)

    # Admin Prefix Command: !serverstats
    @commands.command(name="serverstats", aliases=["stats", "serverinfo"])
    async def serverstats(self, ctx):
        guild = ctx.guild
        total_members = len(guild.members)
        bots = len([m for m in guild.members if m.bot])
        humans = total_members - bots

        embed = discord.Embed(
            title=f"📊 {guild.name} Core Statistics",
            color=0x2ecc71
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Server Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="📅 Created On", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="👥 Member Split", value=f"Total: **{total_members}**\nHumans: **{humans}**\nBots: **{bots}**", inline=False)
        embed.add_field(name="🛡️ Security Level", value=str(guild.verification_level).title(), inline=True)
        embed.add_field(name="🎭 Total Roles", value=f"**{len(guild.roles)}** roles", inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @announce.error
    @prof_announce.error
    async def admin_errors(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Access Denied! This command requires Administrator authorization permissions.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Admin(bot))
