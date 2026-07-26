import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}


    def is_staff():
        async def predicate(ctx):
            return ctx.author.guild_permissions.manage_messages
        return commands.check(predicate)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a member"""

        if member.id not in self.warnings:
            self.warnings[member.id] = []

        self.warnings[member.id].append(reason)

        embed = discord.Embed(
            title="⚠️ Member Warned",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Member",
            value=member.mention
        )

        embed.add_field(
            name="Reason",
            value=reason
        )

        embed.add_field(
            name="Moderator",
            value=ctx.author.mention
        )

        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        """View warnings"""

        warns = self.warnings.get(member.id, [])

        if not warns:
            await ctx.send(
                f"✅ {member.mention} has no warnings."
            )
            return


        embed = discord.Embed(
            title=f"⚠️ Warnings for {member.name}",
            color=discord.Color.red()
        )

        for number, warning in enumerate(warns, start=1):
            embed.add_field(
                name=f"Warning {number}",
                value=warning,
                inline=False
            )

        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clearwarnings(self, ctx, member: discord.Member):
        """Clear warnings"""

        self.warnings.pop(member.id, None)

        await ctx.send(
            f"✅ Cleared warnings for {member.mention}"
        )


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member"""

        await member.kick(reason=reason)

        await ctx.send(
            f"👢 {member.mention} was kicked.\nReason: {reason}"
        )


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member"""

        await member.ban(reason=reason)

        await ctx.send(
            f"🔨 {member.mention} was banned.\nReason: {reason}"
        )


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """Unban a user by ID"""

        user = await self.bot.fetch_user(user_id)

        await ctx.guild.unban(user)

        await ctx.send(
            f"✅ {user} has been unbanned."
        )


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        """Set channel slowmode"""

        await ctx.channel.edit(
            slowmode_delay=seconds
        )

        await ctx.send(
            f"🐢 Slowmode set to {seconds} seconds."
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
