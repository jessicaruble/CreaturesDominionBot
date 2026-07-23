import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! `{latency}ms`")

    @commands.command()
    async def about(self, ctx):
        embed = discord.Embed(
            title="🐉 Creatures of Dominion",
            description="The official Discord bot for the Creatures of Dominion community.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Version", value="1.0.0")
        embed.add_field(name="Developer", value="Creatures of Dominion Team")
        await ctx.send(embed=embed)

    @commands.command()
    async def rules(self, ctx):
        rules = (
            "📜 **Server Rules**\n"
            "1. Be respectful.\n"
            "2. No cheating or exploits.\n"
            "3. No spam.\n"
            "4. Keep chats appropriate.\n"
            "5. Listen to staff."
        )
        await ctx.send(rules)

    @commands.command()
    async def website(self, ctx):
        await ctx.send("🌐 Website coming soon!")

    @commands.command()
    async def server(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.green())
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Channels", value=len(guild.channels))
        embed.add_field(name="Owner", value=str(guild.owner))
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{member}", color=discord.Color.orange())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"))
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"))
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{member.display_name}'s Avatar")
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
