import discord
from discord.ext import commands


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Temporary storage (we will add a database later)
        self.players = {}


    def get_player(self, user):
        if user.id not in self.players:
            self.players[user.id] = {
                "level": 1,
                "xp": 0,
                "coins": 100,
                "dragon_rank": "Novice Trainer",
                "dragons": 0
            }

        return self.players[user.id]


    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        """View player profile"""

        member = member or ctx.author
        player = self.get_player(member)

        embed = discord.Embed(
            title=f"🐉 {member.display_name}'s Profile",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url=member.avatar.url)

        embed.add_field(
            name="⭐ Level",
            value=player["level"],
            inline=True
        )

        embed.add_field(
            name="✨ XP",
            value=player["xp"],
            inline=True
        )

        embed.add_field(
            name="💰 Coins",
            value=player["coins"],
            inline=True
        )

        embed.add_field(
            name="🔥 Dragon Rank",
            value=player["dragon_rank"],
            inline=False
        )

        embed.add_field(
            name="🐲 Dragons Bonded",
            value=player["dragons"],
            inline=False
        )

        await ctx.send(embed=embed)


    @commands.command()
    async def addxp(self, ctx, amount: int):
        """Admin test command to add XP"""

        player = self.get_player(ctx.author)

        player["xp"] += amount

        # Level up every 100 XP
        if player["xp"] >= 100:
            player["xp"] -= 100
            player["level"] += 1

            await ctx.send(
                f"🎉 {ctx.author.mention} leveled up to Level {player['level']}!"
            )

        else:
            await ctx.send(
                f"✨ Added {amount} XP!"
            )


    @commands.command()
    async def rank(self, ctx):
        """Show dragon trainer rank"""

        player = self.get_player(ctx.author)

        await ctx.send(
            f"🔥 {ctx.author.mention}'s Dragon Rank: "
            f"**{player['dragon_rank']}**"
        )


async def setup(bot):
    await bot.add_cog(Profile(bot))
