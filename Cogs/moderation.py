import discord
from discord.ext import commands
import sqlite3
from db_manager import create_profile



class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helper function to save an infraction to the SQLite database
    def log_infraction(self, user_id, guild_id, moderator_id, inf_type, reason):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO infractions (user_id, guild_id, moderator_id, type, reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, guild_id, moderator_id, inf_type, reason))
        conn.commit()
        conn.close()

    # Prefix Command: !warn
    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Issues a formal warning and saves it to the database"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot warn a member with a higher or equal role than yourself.")
            return

        # Save infraction to the DB
        self.log_infraction(member.id, ctx.guild.id, ctx.author.id, "warn", reason)

        # Notify the server
        embed = discord.Embed(
            title="⚠️ Member Warned",
            description=f"**User:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
            color=0xf1c40f
        )
        await ctx.send(embed=embed)

        # Attempt to DM the warned user privately
        try:
            await member.send(f"⚠️ You have been warned in **{ctx.guild.name}** for: {reason}")
        except discord.Forbidden:
            pass # Skips if the user has private messages turned off

    # Prefix Command: !warnings
    @commands.command(name="warnings", aliases=["infractions", "history"])
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        """Looks up a specific member's total warning history"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT moderator_id, type, reason, timestamp 
            FROM infractions 
            WHERE user_id = ? AND guild_id = ?
            ORDER BY timestamp DESC
        ''', (member.id, ctx.guild.id))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await ctx.send(f"✅ {member.mention} has a clean record! No infractions found.")
            return

        embed = discord.Embed(
            title=f"📋 Infraction History for {member.display_name}",
            color=0x34495e
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        # Loop through database entries and add them to the message embed
        for i, row in enumerate(rows, start=1):
            mod_id, inf_type, reason, timestamp = row
            mod = ctx.guild.get_member(mod_id)
            mod_name = mod.mention if mod else f"ID: {mod_id}"
            
            embed.add_field(
                name=f"#{i} | {inf_type.upper()}",
                value=f"**Mod:** {mod_name}\n**Reason:** {reason}\n*Date:* {timestamp}",
                inline=False
            )

        await ctx.send(embed=embed)

    # Prefix Command: !purge
    @commands.command(name="purge", aliases=["clear", "clean"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """Quickly deletes a specific number of recent messages"""
        if amount <= 0:
            await ctx.send("❌ Please specify a number greater than 0.")
            return
            
        # Delete the command message itself + the requested amount
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        # Send a temporary success message that auto-deletes after 3 seconds
        await ctx.send(f"🧹 Successfully cleared **{len(deleted) - 1}** messages.", delete_after=3)

    # Prefix Command: !kick
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Removes a user from the server and logs it"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot kick this member due to role hierarchy.")
            return

        self.log_infraction(member.id, ctx.guild.id, ctx.author.id, "kick", reason)
        await member.kick(reason=reason)

        embed = discord.Embed(
            title="👢 Member Kicked",
            description=f"**User:** {member.name}\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
            color=0xe67e22
        )
        await ctx.send(embed=embed)

    # Prefix Command: !ban
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Permanently bans a user from the server and logs it"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot ban this member due to role hierarchy.")
            return

        self.log_infraction(member.id, ctx.guild.id, ctx.author.id, "ban", reason)
        await member.ban(reason=reason)

        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"**User:** {member.name}\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
