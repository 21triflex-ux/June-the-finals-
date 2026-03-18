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

CLASSES = ["Light","Medium","Heavy"]

WEAPONS = {
    "Light": ["93R", "ARN-220", "Dagger", "LH1", "M11", "M26 Matter", "Recurve Bow", "SH1900", "SR-84", "Sword", "Throwing Knives", "V9S", "XP-54"],
    "Medium": ["AKM", "CB-01 Repeater", "Cerberus 12GA", "CL-40", "Dual Blades", "FAMAS", "FCAR", "Model 1887", "P90", "Pike-556", "R.357", "Riot Shield"],
    "Heavy": [".50 Akimbo", "BFR Titan", "Flamethrower", "KS-23", "Lewis Gun", "M134 Minigun", "M60", "MGL32", "SA1216", "ShAK-50", "Sledgehammer", "Spear"]
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

def generate_random_loadout(player_class=None):

    if not player_class:
        player_class = random.choice(CLASSES)

    weapon = random.choice(WEAPONS[player_class])
    ability = random.choice(ABILITIES[player_class])

    gadgets = random.sample(GADGETS_BY_CLASS[player_class], 3)

    return {
        "class": player_class,
        "weapon": weapon,
        "ability": ability,
        "gadgets": gadgets
    }


def create_embed(loadout, title, ctx):

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


@bot.command(name="loadout", aliases=["random","roll"])
async def random_loadout(ctx):

    loadout = generate_random_loadout()

    embed = create_embed(loadout, "🎲 Random Loadout", ctx)

    await ctx.send(embed=embed)


@bot.command(name="light")
async def random_light(ctx):

    loadout = generate_random_loadout("Light")

    embed = create_embed(loadout, "⚡ Random Light Loadout", ctx)

    await ctx.send(embed=embed)


@bot.command(name="medium")
async def random_medium(ctx):

    loadout = generate_random_loadout("Medium")

    embed = create_embed(loadout, "⚙️ Random Medium Loadout", ctx)

    await ctx.send(embed=embed)


@bot.command(name="heavy")
async def random_heavy(ctx):

    loadout = generate_random_loadout("Heavy")

    embed = create_embed(loadout, "💪 Random Heavy Loadout", ctx)

    await ctx.send(embed=embed)


@bot.command(name="team")
async def random_team(ctx):

    embed = discord.Embed(
        title="🎲 Random Team Loadouts",
        color=discord.Color.purple(),
        timestamp=ctx.message.created_at
    )

    for i in range(1,4):

        loadout = generate_random_loadout()

        value = (
            f"Class: **{loadout['class']}**\n"
            f"Weapon: {loadout['weapon']}\n"
            f"Ability: {loadout['ability']}\n"
            f"Gadgets:\n" + "\n".join(f"• {g}" for g in loadout["gadgets"])
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
