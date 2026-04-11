import discord
from discord.ext import commands
from discord.ui import View, button
import logging
from dotenv import load_dotenv
import os
import random
import webserver

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

CLASSES = ["Light", "Medium", "Heavy"]
WEAPONS = {
    "Light": ["93R","ARN-220","Dagger","LH1","M11","M26 Matter","Recurve Bow","SH1900","SR-84","Sword","Throwing Knives","V9S","XP-54"],
    "Medium": ["AKM","CB-01 Repeater","Cerberus 12GA","CL-40","Dual Blades","FAMAS","FCAR","Model 1887","P90","Pike-556","R.357","Riot Shield","Chimera-XB"],
    "Heavy": [".50 Akimbo","BFR Titan","Flamethrower","KS-23","Lewis Gun","M134 Minigun","M60","MGL32","SA1216","ShAK-50","Sledgehammer","Spear"]
}
ABILITIES = {
    "Light": ["Cloaking Device","Evasive Dash","Grappling Hook"],
    "Medium": ["Healing Beam","Dematerializer","Guardian Turret","Shock Wave"],
    "Heavy": ["Charge 'N' Slam","Mesh Shield","Goo Gun","Winch Claw"]
}
GADGETS_BY_CLASS = {
    "Light": ["Breach Charge","Gateway","Glitch Grenade","Gravity Vortex","H+ Infuser","Sonar Grenade","Nullifier","Thermal Bore","Tracking Dart","Vanishing Bomb","Flashbang","Frag Grenade","Gas Grenade","Goo Grenade","Pyro Grenade","Smoke Grenade"],
    "Medium": ["APS Turret","Breach Drill","Data Reshaper","Defibrillator","Explosive Mine","Gas Mine","Glitch Trap","Jump Pad","Zipline","Proximity Sensor","Flashbang","Frag Grenade","Gas Grenade","Goo Grenade","Pyro Grenade","Smoke Grenade","Hover Pad"],
    "Heavy": ["Anti-Gravity Cube","Barricade","C4","Dome Shield","Explosive Mine","Healing Emitter","Proximity Sensor","Lockbolt","Pyro Mine","RPG-7","Flashbang","Frag Grenade","Gas Grenade","Goo Grenade","Pyro Grenade","Smoke Grenade"]
}

def generate_loadout(player_class):
    weapon = random.choice(WEAPONS[player_class])
    ability = random.choice(ABILITIES[player_class])
    gadgets = random.sample(GADGETS_BY_CLASS[player_class], 3)
    return {"class": player_class, "weapon": weapon, "ability": ability, "gadgets": gadgets}

def random_loadout():
    return generate_loadout(random.choice(CLASSES))

def format_loadout(l):
    return (
        f"Class: **{l['class']}**\n"
        f"Weapon: {l['weapon']}\n"
        f"Ability: {l['ability']}\n"
        f"Gadgets:\n" +
        "\n".join(f"• {g}" for g in l["gadgets"])
    )

def build_embed(loadout, title, ctx):
    embed = discord.Embed(title=title, color=discord.Color.blue(), timestamp=ctx.message.created_at)
    embed.add_field(name="Class", value=f"**{loadout['class']}**", inline=False)
    embed.add_field(name="Weapon", value=loadout["weapon"], inline=True)
    embed.add_field(name="Ability", value=loadout["ability"], inline=True)
    embed.add_field(name="Gadgets", value="\n".join(f"• {g}" for g in loadout["gadgets"]), inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
    return embed

# ── INTERACTIVE TEAM LOBBY ──
class TeamView(View):
    def __init__(self, num_teams, host, with_loadouts=True, initial_players=None):
        super().__init__(timeout=1800)
        self.players = set(initial_players) if initial_players else set()
        self.num_teams = num_teams
        self.host = host
        self.with_loadouts = with_loadouts
        self.lobby_title = "🎮 Team Lobby" if with_loadouts else "👥 People Lobby"
        self.lobby_message = None
        self.results_message = None

    def get_lobby_embed(self):
        player_list = "\n".join([p.mention for p in self.players]) or "No players yet"
        return discord.Embed(
            title=self.lobby_title,
            description=f"**Teams:** {self.num_teams}\n\n**Players ({len(self.players)}):**\n{player_list}",
            color=discord.Color.blue()
        )

    async def update_message(self, interaction):
        embed = self.get_lobby_embed()
        await interaction.message.edit(embed=embed, view=self)

    async def refresh_lobby(self):
        if self.lobby_message:
            embed = self.get_lobby_embed()
            await self.lobby_message.edit(embed=embed, view=self)

    @button(label="Join", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("You're already in!", ephemeral=True)
            return
        self.players.add(interaction.user)
        await interaction.response.defer()
        await self.update_message(interaction)

    @button(label="Leave", style=discord.ButtonStyle.red)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            await interaction.response.send_message("You're not in!", ephemeral=True)
            return
        self.players.remove(interaction.user)
        await interaction.response.defer()
        await self.update_message(interaction)

    @button(label="Done", style=discord.ButtonStyle.blurple)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host:
            await interaction.response.send_message("Only the host can start!", ephemeral=True)
            return
        if len(self.players) < 2:
            await interaction.response.send_message("Not enough players!", ephemeral=True)
            return

        players_list = list(self.players)
        random.shuffle(players_list)
        teams = [[] for _ in range(self.num_teams)]
        for i, player in enumerate(players_list):
            teams[i % self.num_teams].append(player)

        if self.with_loadouts:
            embed = discord.Embed(title=f"🔥 {self.num_teams} Teams + Loadouts 🔥", color=discord.Color.orange())
        else:
            embed = discord.Embed(title=f"👥 {self.num_teams} Teams Split 👥", color=discord.Color.orange())

        for i, team in enumerate(teams, start=1):
            text = ""
            for user in team:
                if self.with_loadouts:
                    l = random_loadout()
                    text += f"{user.mention}\n{format_loadout(l)}\n\n"
                else:
                    text += f"{user.mention}\n\n"
            embed.add_field(name=f"Team {i}", value=text, inline=False)

        await interaction.response.defer()
        await self.results_message.edit(embed=embed)

# ── SIMPLE RSP ROSTER (Join/Leave only) ──
class RSPView(View):
    def __init__(self, initial_players=None):
        super().__init__(timeout=None)
        self.players = set(initial_players) if initial_players else set()
        self.message = None

    def get_embed(self):
        player_list = "\n".join([p.mention for p in self.players]) or "No players yet"
        return discord.Embed(
            title="📋 RSP List",
            description=f"**Players ({len(self.players)}):**\n{player_list}\n\nClick **Join** or **Leave** below!",
            color=discord.Color.green()
        )

    async def update(self):
        if self.message:
            embed = self.get_embed()
            await self.message.edit(embed=embed, view=self)

    @button(label="Join", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("You're already in!", ephemeral=True)
            return
        self.players.add(interaction.user)
        await interaction.response.defer()
        await self.update()

    @button(label="Leave", style=discord.ButtonStyle.red)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            await interaction.response.send_message("You're not in!", ephemeral=True)
            return
        self.players.remove(interaction.user)
        await interaction.response.defer()
        await self.update()

# ── COMMANDS ──
@bot.command(aliases=["random","roll"])
async def loadout(ctx):
    l = random_loadout()
    await ctx.send(embed=build_embed(l, "🎲 Random Loadout", ctx))

@bot.command()
async def light(ctx):
    await ctx.send(embed=build_embed(generate_loadout("Light"), "⚡ Random Light Loadout", ctx))

@bot.command()
async def medium(ctx):
    await ctx.send(embed=build_embed(generate_loadout("Medium"), "⚙️ Random Medium Loadout", ctx))

@bot.command()
async def heavy(ctx):
    await ctx.send(embed=build_embed(generate_loadout("Heavy"), "💪 Random Heavy Loadout", ctx))

@bot.command()
async def teams(ctx, num_teams: int):
    if num_teams < 2:
        await ctx.send("You need at least 2 teams!")
        return
    initial = ctx.message.mentions
    view = TeamView(num_teams, ctx.author, with_loadouts=True, initial_players=initial)

    lobby_embed = view.get_lobby_embed()
    lobby_msg = await ctx.send(embed=lobby_embed, view=view)
    view.lobby_message = lobby_msg

    results_embed = discord.Embed(
        title="🔥 Team Results 🔥",
        description="Click **Done** in the lobby above to generate teams!",
        color=discord.Color.orange()
    )
    results_msg = await ctx.send(embed=results_embed)
    view.results_message = results_msg

    bot.active_view = view

@bot.command()
async def people(ctx, num_teams: int):
    if num_teams < 2:
        await ctx.send("You need at least 2 teams!")
        return
    initial = ctx.message.mentions
    view = TeamView(num_teams, ctx.author, with_loadouts=False, initial_players=initial)

    lobby_embed = view.get_lobby_embed()
    lobby_msg = await ctx.send(embed=lobby_embed, view=view)
    view.lobby_message = lobby_msg

    results_embed = discord.Embed(
        title="👥 Team Split Results 👥",
        description="Click **Done** in the lobby above to split teams!",
        color=discord.Color.orange()
    )
    results_msg = await ctx.send(embed=results_embed)
    view.results_message = results_msg

    bot.active_view = view

@bot.command()
async def add(ctx):
    """Add people to the current lobby (deletes your command message)"""
    if not hasattr(bot, 'active_view') or not bot.active_view:
        await ctx.send("❌ No active lobby! Run `$teams` or `$people` first.", delete_after=10)
        await ctx.message.delete()
        return

    mentions = ctx.message.mentions
    if not mentions:
        await ctx.send("❌ Mention at least one user to add!", delete_after=8)
        await ctx.message.delete()
        return

    added = 0
    for user in mentions:
        if user not in bot.active_view.players:
            bot.active_view.players.add(user)
            added += 1

    await bot.active_view.refresh_lobby()
    await ctx.send(f"✅ Added **{added}** player(s)!", delete_after=8)
    await ctx.message.delete()

@bot.command()
async def remove(ctx):
    """Remove people from the current lobby (deletes your command message)"""
    if not hasattr(bot, 'active_view') or not bot.active_view:
        await ctx.send("❌ No active lobby! Run `$teams` or `$people` first.", delete_after=10)
        await ctx.message.delete()
        return

    mentions = ctx.message.mentions
    if not mentions:
        await ctx.send("❌ Mention at least one user to remove!", delete_after=8)
        await ctx.message.delete()
        return

    removed = 0
    for user in mentions:
        if user in bot.active_view.players:
            bot.active_view.players.remove(user)
            removed += 1

    await bot.active_view.refresh_lobby()
    await ctx.send(f"✅ Removed **{removed}** player(s)!", delete_after=8)
    await ctx.message.delete()

@bot.command()
async def rsp(ctx):
    """Simple persistent RSP roster (Join/Leave only)"""
    initial = ctx.message.mentions
    view = RSPView(initial_players=initial)
    embed = view.get_embed()
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg

@bot.command()
async def scrim(ctx):
    embed = discord.Embed(title="🏆 Scrim Mode (Balanced Team)", color=discord.Color.gold(), timestamp=ctx.message.created_at)
    for i, c in enumerate(["Light", "Medium", "Heavy"], start=1):
        l = generate_loadout(c)
        embed.add_field(name=f"Player {i}", value=format_loadout(l), inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

if __name__ == "__main__":
    webserver.keep_alive()
    if not token:
        raise ValueError("DISCORD_TOKEN not found in environment variables")
    bot.run(token, log_handler=handler)
