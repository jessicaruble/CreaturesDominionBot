import discord
from discord.ext import commands

# 1. This defines the interactive button inside the private ticket channel to close it
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🧹 Closing this ticket channel in 5 seconds...", ephemeral=False)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.datetime.timedelta(seconds=5))
        await interaction.channel.delete(reason="Ticket closed by staff/user.")

# 2. This defines the main landing panel button used to open a ticket
class TicketLandingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Create Support Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Check if a ticket channel for this user already exists to prevent duplicate spam
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"❌ You already have an open ticket here: {existing_channel.mention}", ephemeral=True)
            return

        # Define private override permissions for the new ticket room
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False), # Hides from public
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True), # Shows to user
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True) # Shows to bot
        }

        # Look for a staff/moderator role to give them access to the ticket automatically
        staff_role = discord.utils.get(guild.roles, name="Staff") or discord.utils.get(guild.roles, name="Moderator")
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        # Create the private text channel
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            overwrites=overwrites,
            reason=f"Ticket opened by {user.name}"
        )

        # Send a welcoming control panel inside the new private room
        embed = discord.Embed(
            title=f"🎟️ Ticket — Welcome {user.display_name}",
            description="Thank you for reaching out! State your request or question clearly here. A staff member will assist you shortly.\n\nTo lock and archive this channel, click the red button below.",
            color=0x2ecc71
        )
        await ticket_channel.send(content=f"{user.mention} | {staff_role.mention if staff_role else ''}", embed=embed, view=CloseTicketView())
        
        # Acknowledge the initial button click to the user privately
        await interaction.response.send_message(f"✅ Ticket created successfully! Head over to {ticket_channel.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Admin Prefix Command to position the button launcher anywhere in the server
    @commands.command(name="setup_tickets")
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        """Spawns the support ticket button launch panel"""
        embed = discord.Embed(
            title="⚔️ Support & Help Desk ⚔️",
            description="Do you need to contact the Dominion Staff team? Click the button below to generate a secure, private text channel where you can chat with us directly.",
            color=0x9b59b6
        )
        await ctx.send(embed=embed, view=TicketLandingView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
