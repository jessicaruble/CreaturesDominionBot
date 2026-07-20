import discord
from discord.ext import commands
import asyncio
import random

# Interactive button view for entering active giveaways
class GiveawayJoinView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Keeps button active indefinitely
        self.entrants = set() # Unique set tracking user IDs

    @discord.ui.button(label="🎉 Enter Giveaway", style=discord.ButtonStyle.success, custom_id="join_giveaway_btn")
    async def join_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        if user_id in self.entrants:
            await interaction.response.send_message("❌ You have already entered this giveaway!", ephemeral=True)
        else:
            self.entrants.add(user_id)
            await interaction.response.send_message(f"🎉 Success! You have entered the drawing. Total entrants: **{len(self.entrants)}**", ephemeral=True)

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_view = None # Keeps track of the current active view instance

    # Admin Prefix Command: !giveaway [time_in_seconds] [prize text]
    @commands.command(name="giveaway", aliases=["gstart", "host"])
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx, duration: int, *, prize: str):
        """Starts an automated countdown giveaway with interactive entry buttons"""
        if duration <= 0:
            await ctx.send("❌ Duration must be a positive number of seconds!")
            return

        # Initialize the button view handler
        self.active_view = GiveawayJoinView()

        embed = discord.Embed(
            title="🎉 NEW DOMINION GIVEAWAY! 🎉",
            description=f"**Prize:** {prize}\n**Hosted By:** {ctx.author.mention}\n\nClick the green button below to enter the drawing!",
            color=0x9b59b6
        )
        embed.add_field(name="Time Remaining", value=f"⏳ **{duration} seconds**", inline=False)
        embed.set_footer(text="Good luck to all adventurers!")

        giveaway_msg = await ctx.send(embed=embed, view=self.active_view)

        # Countdown loop updating the timer display
        time_left = duration
        while time_left > 0:
            await asyncio.sleep(min(5, time_left)) # Update every 5 seconds to comply with rate limits
            time_left -= min(5, time_left)
            
            # Update embed text
            if time_left > 0:
                embed.set_field_at(0, name="Time Remaining", value=f"⏳ **{time_left} seconds**", inline=False)
                try:
                    await giveaway_msg.edit(embed=embed)
                except discord.NotFound:
                    return # Stop if the message gets deleted mid-giveaway

        # --- GIVEAWAY CONCLUSION ---
        # Disable the entry button
        for child in self.active_view.children:
            child.disabled = True
        
        winners_pool = list(self.active_view.entrants)

        if not winners_pool:
            embed.title = "🎉 GIVEAWAY ENDED 🎉"
            embed.set_field_at(0, name="Result", value="❌ No one entered the giveaway, so no winner could be drawn.", inline=False)
            await giveaway_msg.edit(embed=embed, view=self.active_view)
            await ctx.send(f"❌ The giveaway for **{prize}** ended with zero entries.")
            return

        # Pick a random winner from the pool
        winner_id = random.choice(winners_pool)
        winner = ctx.guild.get_member(winner_id) or await self.bot.fetch_user(winner_id)

        embed.title = "🎉 GIVEAWAY CONCLUDED 🎉"
        embed.set_field_at(0, name="✨ Winner ✨", value=f"🏆 {winner.mention} has won the **{prize}**!", inline=False)
        embed.set_footer(text=f"Total Participants: {len(winners_pool)}")
        
        await giveaway_msg.edit(embed=embed, view=self.active_view)
        await ctx.send(f"🥳 Congratulations {winner.mention}! You won the drawing for **{prize}**!")

    @giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing parameters! Correct format: `!giveaway [seconds] [prize]` \nExample: `!giveaway 30 1000_Coins` ")

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
