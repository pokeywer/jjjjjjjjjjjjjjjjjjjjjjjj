import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import qrcode
from io import BytesIO
from datetime import timedelta
import requests
import os

TOKEN = os.environ.get("DISCORD_TOKEN")
Prefix = "!"
SERVER_ID = 1383109081371508870

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class EliteBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=SERVER_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("LXNCE LXNCE THE GOAT")

bot = EliteBot()


def is_admin():
    async def predicate(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need **Administrator** permission.", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)


@bot.tree.command(name="ping", description="Bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! `{latency}ms`")

@bot.tree.command(name="avatar", description="Show avatar")
@app_commands.describe(user="User (default: you)")
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    user = user or interaction.user
    embed = discord.Embed(color=0x2b2d31)
    embed.set_author(name=f"{user.name}'s Avatar", icon_url=user.display_avatar.url)
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="User information")
@app_commands.describe(user="User (default: you)")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title="User Info", color=0x2b2d31)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Name", value=user.display_name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Joined", value=user.joined_at.strftime("%d %b %Y"), inline=True)
    embed.add_field(name="Created", value=user.created_at.strftime("%d %b %Y"), inline=True)
    embed.add_field(name="Top Role", value=user.top_role.mention if user.top_role != user.guild.default_role else "None", inline=True)
    embed.add_field(name="Boosting", value="Yes" if user.premium_since else "No", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Server stats")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=f"{g.name}", color=0x2b2d31)
    embed.add_field(name="Members", value=g.member_count, inline=True)
    embed.add_field(name="Channels", value=len(g.channels), inline=True)
    embed.add_field(name="Roles", value=len(g.roles), inline=True)
    embed.add_field(name="Owner", value=g.owner.mention, inline=True)
    embed.add_field(name="Created", value=g.created_at.strftime("%d %b %Y"), inline=True)
    embed.add_field(name="Boosts", value=f"Level {g.premium_tier} ({g.premium_subscription_count})", inline=True)
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="qr", description="Generate QR code")
@app_commands.describe(text="Text/URL to encode")
async def qr(interaction: discord.Interaction, text: str):
    qr_img = qrcode.make(text)
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)
    await interaction.response.send_message(file=discord.File(buf, "qr.png"))

@bot.tree.command(name="8ball", description="Magic 8-ball")
@app_commands.describe(question="Your question")
async def eightball(interaction: discord.Interaction, question: str):
    answers = ["Yes", "No", "Maybe", "Ask again", "Definitely", "Never", "Outlook good", "Cannot predict"]
    await interaction.response.send_message(f"🎱 **{question}**\n→ {random.choice(answers)}")

@bot.tree.command(name="roll", description="Roll dice")
@app_commands.describe(sides="Number of sides")
async def roll(interaction: discord.Interaction, sides: int = 6):
    if sides < 2: sides = 6
    await interaction.response.send_message(f"🎲 Rolled **{random.randint(1, sides)}** (1-{sides})")

@bot.tree.command(name="coin", description="Flip a coin")
async def coin(interaction: discord.Interaction):
    await interaction.response.send_message(f"🪙 **{random.choice(['Heads', 'Tails'])}**")

@bot.tree.command(name="poll", description="Create poll")
@app_commands.describe(question="Poll question")
async def poll(interaction: discord.Interaction, question: str):
    msg = await interaction.response.send_message(f"📊 **{question}**\n\n✅ Yes\n❌ No")
    message = await interaction.original_response()
    await message.add_reaction("✅")
    await message.add_reaction("❌")


@bot.tree.command(name="roleadd", description="Give roles to a user (Admin only)")
@app_commands.describe(
    member="The user to whitelist",
    role1="First role (required)",
    role2="Second role (optional)",
    role3="Third role (optional)",
    role4="Fourth role (optional)",
    role5="Fifth role (optional)"
)
@is_admin()
async def whitelist(
    interaction: discord.Interaction,
    member: discord.Member,
    role1: discord.Role,
    role2: discord.Role = None,
    role3: discord.Role = None,
    role4: discord.Role = None,
    role5: discord.Role = None
):
    roles_to_add = [r for r in [role1, role2, role3, role4, role5] if r is not None]

    added_roles = []
    failed_roles = []

    for role in roles_to_add:
        if role in member.roles:
            failed_roles.append(f"{role.mention} (already has)")
        else:
            try:
                await member.add_roles(role, reason=f"Whitelisted by {interaction.user}")
                added_roles.append(role.mention)
            except:
                failed_roles.append(f"{role.mention} (no permission)")

    embed = discord.Embed(title="Whitelist Result", color=0x00ff00 if added_roles else 0xff0000)
    embed.add_field(name="User", value=member.mention, inline=False)
    if added_roles:
        embed.add_field(name="Added Roles", value="\n".join(added_roles), inline=False)
    if failed_roles:
        embed.add_field(name="Failed/Skipped", value="\n".join(failed_roles), inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="clear", description="Clear messages")
@app_commands.describe(amount="1-500")
@is_admin()
async def clear(interaction: discord.Interaction, amount: int = 50):
    if not 1 <= amount <= 500:
        return await interaction.response.send_message("1-500 only.", ephemeral=True)
    await interaction.channel.purge(limit=amount + 1)
    await interaction.response.send_message(f"Cleared {amount} messages.", ephemeral=True)

@bot.tree.command(name="kick", description="Kick member")
@app_commands.describe(member="Member", reason="Reason")
@is_admin()
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.mention}")
    except:
        await interaction.response.send_message("Failed.", ephemeral=True)

@bot.tree.command(name="ban", description="Ban member")
@app_commands.describe(member="Member", reason="Reason")
@is_admin()
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"Banned {member.mention}")
    except:
        await interaction.response.send_message("Failed.", ephemeral=True)

@bot.tree.command(name="mute", description="Mute member")
@app_commands.describe(member="Member", minutes="Minutes")
@is_admin()
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int = 10):
    try:
        await member.timeout(discord.utils.utcnow() + timedelta(minutes=minutes))
        await interaction.response.send_message(f"Muted {member.mention} for {minutes}m")
    except:
        await interaction.response.send_message("Failed.", ephemeral=True)

@bot.tree.command(name="unmute", description="Unmute member")
@app_commands.describe(member="Member")
@is_admin()
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not member.is_timed_out():
        return await interaction.response.send_message("Not muted.", ephemeral=True)
    await member.timeout(None)
    await interaction.response.send_message(f"Unmuted {member.mention}")

@bot.tree.command(name="slowmode", description="Set slowmode")
@app_commands.describe(seconds="0-21600")
@is_admin()
async def slowmode(interaction: discord.Interaction, seconds: int = 0):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"Slowmode: {seconds}s")

@bot.tree.command(name="lock", description="Lock channel")
@is_admin()
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("Channel locked 🔒")

@bot.tree.command(name="unlock", description="Unlock channel")
@is_admin()
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
    await interaction.response.send_message("Channel unlocked 🔓")

@bot.tree.command(name="status", description="Change bot status")
@app_commands.describe(text="Status text")
@is_admin()
async def status(interaction: discord.Interaction, text: str):
    await bot.change_presence(activity=discord.Game(name=text))
    await interaction.response.send_message(f"Status set: {text}")

@bot.tree.command(name="shutdown", description="Shutdown bot")
@is_admin()
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("Shutting down...")
    await bot.close()

@bot.tree.command(name="dm", description="DM a member (Admin only)")
@app_commands.describe(member="The member to DM", message="Message to send")
@is_admin()
async def dm(interaction: discord.Interaction, member: discord.Member, message: str):
    try:
        await member.send(message)
        await interaction.response.send_message("✅ DM sent successfully!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Failed to DM — user has DMs disabled or blocked the bot.", ephemeral=True)
    except Exception:
        await interaction.response.send_message("❌ Failed to send DM (unknown error).", ephemeral=True)

@bot.tree.command(name="nuke", description="Nuke channel")
@is_admin()
async def nuke(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    new = await interaction.channel.clone()
    await interaction.channel.delete()
    await new.send("💥 Channel nuked by admin!")
    await interaction.followup.send("Nuke complete.", ephemeral=True)

@bot.tree.command(name="embed", description="Send custom embed")
@app_commands.describe(title="Title", description="Description")
@is_admin()
async def embed(interaction: discord.Interaction, title: str, description: str):
    await interaction.response.send_message(embed=discord.Embed(title=title, description=description, color=0xff0000))

@bot.tree.command(name="warn", description="Fake warn member")
@app_commands.describe(member="Member")
@is_admin()
async def warn(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"⚠️ {member.mention} has been warned!")

@bot.tree.command(name="hackban", description="Ban user not in server")
@app_commands.describe(user_id="User ID")
@is_admin()
async def hackban(interaction: discord.Interaction, user_id: str):
    await interaction.guild.ban(discord.Object(id=int(user_id)))
    await interaction.response.send_message(f"Banned {user_id}")

@bot.tree.command(name="nick", description="Change nickname")
@app_commands.describe(member="Member", nickname="New nickname")
@is_admin()
async def nick(interaction: discord.Interaction, member: discord.Member, nickname: str):
    await member.edit(nick=nickname)
    await interaction.response.send_message(f"Nickname set for {member.mention}")

@bot.tree.command(name="unban", description="Unban by user ID")
@app_commands.describe(user_id="User ID")
@is_admin()
async def unban(interaction: discord.Interaction, user_id: str):
    try: await interaction.guild.unban(discord.Object(id=int(user_id))); await interaction.response.send_message(f"Unbanned {user_id}")
    except: await interaction.response.send_message("Failed.", ephemeral=True)

@bot.tree.command(name="say", description="Make the bot repeat your message")
@app_commands.describe(message="What to say")
async def say_public(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("Sent!", ephemeral=True)
    await interaction.channel.send(message)

@bot.tree.command(name="massmove", description="Mass move voice members")
@app_commands.describe(source="From VC", target="To VC")
@is_admin()
async def massmove(interaction: discord.Interaction, source: discord.VoiceChannel, target: discord.VoiceChannel):
    count = 0
    for m in source.members:
        try: await m.move_to(target); count += 1
        except: pass
    await interaction.response.send_message(f"Moved {count} members")

@bot.tree.command(name="fakeraid", description="Fake raid warning (fun)")
@is_admin()
async def fakeraid(interaction: discord.Interaction):
    await interaction.response.send_message("Sent!", ephemeral=True)
    await interaction.channel.send(
        "🚨 **RAID DETECTED** 🚨\n"
        "||@everyone||\n"
        "Server under attack!\n"
        "Lock channels and stay calm!\n"
        "*(this is a test)*"
    )

@bot.tree.command(name="servericon", description="Change server icon")
@app_commands.describe(image_url="Direct image URL")
@is_admin()
async def servericon(interaction: discord.Interaction, image_url: str):
    try:
        r = requests.get(image_url, timeout=10)
        await interaction.guild.edit(icon=r.content)
        await interaction.response.send_message("Server icon updated!")
    except:
        await interaction.response.send_message("Failed (invalid URL or permission)", ephemeral=True)

@bot.tree.command(name="boostcount", description="Show current boost status")
@is_admin()
async def boostcount(interaction: discord.Interaction):
    g = interaction.guild
    await interaction.response.send_message(
        f"**Boost Status**\n"
        f"Level: {g.premium_tier}\n"
        f"Boosts: {g.premium_subscription_count}\n"
        f"Needed for next level: {g.premium_tier * 7 + 7 if g.premium_tier < 3 else 'Max'}"
    )

@bot.tree.command(name="dog", description="Random dog picture")
async def dog(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        r = requests.get("https://dog.ceo/api/breeds/image/random")
        data = r.json()
        embed = discord.Embed(title="🐶 Woof!", color=0x2b2d31)
        embed.set_image(url=data['message'])
        await interaction.followup.send(embed=embed)
    except:
        await interaction.followup.send("Couldn't fetch a doggo 😢")

@bot.event
async def on_message(message):
    
    if message.author.bot:
        return

    
    if message.content.strip().lower() == "!goat":
       
        if message.guild and message.guild.id == SERVER_ID:
            await message.channel.send("LXNCE!")

    
    await bot.process_commands(message)



bot.run(TOKEN)
