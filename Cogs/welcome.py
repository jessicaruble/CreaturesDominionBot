import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. EVENT: Triggered when a new user joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        
        # Look for a text channel named 'welcome', 'general', or 'chat' to greet them
        welcome_channel = discord.utils.get(guild.text_channels, name="welcome") or \
                          discord.utils.get(guild.text_channels, name="general") or \
                          guild.text_channels[0] # Fallback to first available channel

        if welcome_channel:
            embed = discord.Embed(
                title=f"👋 Welcome to {guild.name}!",
                description=f"Hail traveler {member.mention}! Welcome to the Creatures Dominion.\n\n"
                            f"✨ **Step 1:** Go to the verification channel and verify!\n"
                            f"⚔️ **Step 2:** Pick your faction and start your adventure!",
                color=0x2ecc71
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)
            embed.add_field(name="Member Count", value=f"#{len(guild.members)}", inline=True)
            embed.set_footer(text=f"ID: {member.id}")
            
            # Send the welcome greeting card
            await welcome_channel.send(content=member.mention, embed=embed)

        # OPTIONAL AUTO-ROLE: Automatically give them an "Unverified" or "Member" role on join
        auto_role = discord.utils.get(guild.roles, name="Unverified")
        if auto_role:
            try:
                await member.add_roles(auto_role)
            except discord.Forbidden:
                pass # Fails silently if bot role position is too low in hierarchy

    # 2. EVENT: Triggered when a member leaves the server
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        
        # Look for a text channel named 'leave', 'goodbye', or fallback
        leave_channel = discord.utils.get(guild.text_channels, name="leave") or \
                        discord.utils.get(guild.text_channels, name="goodbye") or \
                        discord.utils.get(guild.text_channels, name="welcome")

        if leave_channel:
            embed = discord.Embed(
                title="😢 A Traveler Has Left",
                description=f"**{member.name}** has crossed back over the border and left the dominion.",
                color=0xe74c3c
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Remaining Members: {len(guild.members)}")
            
            await leave_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
