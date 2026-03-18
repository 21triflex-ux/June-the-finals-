import discord
from discord.ext import commands
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
    "Medium": ["AKM","CB-01 Repeater","Cerberus 12GA","CL-40","Dual Blades","FAMAS","FCAR","Model 1887","P90","Pike-556","R.357","Riot Shield"],
    "Heavy": [".50 Akimbo","BFR Titan","Flamethrower","KS-23","Lewis Gun","M134 Minigun","M60","MGL32","SA1216","ShAK-50","Sledgehammer","Spear"]
}

ABILITIES = {
    "Light": ["Cloaking Device","Evasive Dash","Grappling Hook"],
    "Medium": ["Healing Beam","Dematerializer","Guardian Turret","Recon Senses"],
    "Heavy": ["Charge 'N' Slam","Mesh Shield","Goo Gun","Winch Claw"]
}

GADGETS_BY_CLASS = {
    "Light": [
        "Breach Charge","Gateway","Glitch Grenade","Gravity Vortex","H+ Infuser","Sonar Grenade",
        "Nullifier","Thermal Bore","Thermal Vision","Tracking Dart","Vanishing Bomb",
        "Flashbang","Frag Grenade","Gas Grenade","Goo Grenade","Pyro Grenade","Smoke Grenade"
    ],
    "Medium": [
        "APS Turret","Breach Drill","Data Reshaper","Defibrillator","Explosive Mine","Gas Mine",
        "Glitch Trap","Jump Pad","Zipline","Proximity Sensor",
        "Flashbang","Frag Grenade","Gas Grenade","Goo Grenade","Pyro Grenade","Smoke Grenade"
    ],
    "Heavy": [
        "Anti-Gravity Cube","Barricade","C4","Dome Shield","Explosive Mine","Healing Emitter",
        "Proximity Sensor","Lockbolt","Pyro Mine","RPG-7",
        "Flashbang","Frag Grenade","Gas Grenade","Goo Grenade","Pyro Grenade","Smoke Grenade"
    ]
}


def generate_loadout(player_class):

    weapon = random.choice(WEAPONS[player_class])
    ability = random.choice(ABILITIES[player_class])
    gadgets = random.sample(GADGETS_BY_CLASS[player_class], 3)

    return {
        "class": player_class,
        "weapon": weapon,
        "ability": ability,
        "gadgets": gadgets
    }


def random_loadout():
    return generate_loadout(random.choice(CLASSES))


def build_embed(loadout, title, ctx):

    embed = discord.Embed(
        title=title,
        color=discord.Color.blue(),
        timestamp=ctx.message.created_at
    )

    embed.add_field(name="Class", value=f"**{loadout['class']}**", inline=False)
    embed.add_field(name="Weapon", value=loadout["weapon"], inline=True)
    embed.add_field(name="Ability", value=loadout["ability"], inline=True)

    embed.add_field(
        name="Gadgets",
        value="\n".join(f"• {g}" for g in loadout["gadgets"]),
        inline=False
    )

    embed.set_footer(text=f"Requested by {ctx.author.display_name}")

    return embed


@bot.command(aliases=["random","roll"])
async def loadout(ctx):

    l = random_loadout()
    await ctx.send(embed=build_embed(l, "🎲 Random Loadout", ctx))


@bot.command()
async def light(ctx):

    l = generate_loadout("Light")
    await ctx.send(embed=build_embed(l, "⚡ Random Light Loadout", ctx))


@bot.command()
async def medium(ctx):

    l = generate_loadout("Medium")
    await ctx.send(embed=build_embed(l, "⚙️ Random Medium Loadout", ctx))


@bot.command()
async def heavy(ctx):

    l = generate_loadout("Heavy")
    await ctx.send(embed=build_embed(l, "💪 Random Heavy Loadout", ctx))


@bot.command()
async def team(ctx):

    embed = discord.Embed(
        title="🎲 Random Team Loadouts",
        color=discord.Color.purple(),
        timestamp=ctx.message.created_at
    )

    for i in range(1,4):

        l = random_loadout()

        value = (
            f"Class: **{l['class']}**\n"
            f"Weapon: {l['weapon']}\n"
            f"Ability: {l['ability']}\n"
            f"Gadgets:\n" +
            "\n".join(f"• {g}" for g in l["gadgets"])
        )

        embed.add_field(name=f"Player {i}", value=value, inline=False)

    embed.set_footer(text=f"Requested by {ctx.author.display_name}")

    await ctx.send(embed=embed)


@bot.command()
async def scrim(ctx):

    embed = discord.Embed(
        title="🏆 Scrim Mode (Balanced Team)",
        color=discord.Color.gold(),
        timestamp=ctx.message.created_at
    )

    classes = ["Light", "Medium", "Heavy"]

    for i, c in enumerate(classes, start=1):

        l = generate_loadout(c)

        value = (
            f"Class: **{l['class']}**\n"
            f"Weapon: {l['weapon']}\n"
            f"Ability: {l['ability']}\n"
            f"Gadgets:\n" +
            "\n".join(f"• {g}" for g in l["gadgets"])
        )

        embed.add_field(name=f"Player {i}", value=value, inline=False)

    embed.set_footer(text=f"Requested by {ctx.author.display_name}")

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
