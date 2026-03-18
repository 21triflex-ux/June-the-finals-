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
        "Breach Charge", "Gateway", "Glitch Grenade", "Gravity Vortex", "H+ Infuser", "Sonar Grenade", "Nullifier", "Thermal Bore", "Thermal Vision", "Tracking Dart", "Vanishing Bomb","Flashbang", "Frag Grenade", "Gas Grenade", "Goo Grenade", "Pyro Grenade", "Smoke Grenade"],
    "Medium": [
        "APS Turret", "Breach Drill", "Data Reshaper", "Defibrillator", "Explosive Mine", "Gas Mine", "Glitch Trap", "Jump Pad", "Zipline", "Proximity Sensor","Flashbang", "Frag Grenade", "Gas Grenade", "Goo Grenade", "Pyro Grenade", "Smoke Grenade"],
    "Heavy": [
        "Anti-Gravity Cube", "Barricade", "C4", "Dome Shield", "Explosive Mine", "Healing Emitter", "Proximity Sensor", "Lockbolt", "Pyro Mine", "RPG-7","Flashbang", "Frag Grenade", "Gas Grenade", "Goo Grenade", "Pyro Grenade", "Smoke Grenade"]
}
def generate_random_loadout():
    player_class = random.choice(CLASSES)
    weapon = random.choice(WEAPONS.get(player_class, ["No weapons defined"]))
    ability = random.choice(ABILITIES.get(player_class, ["No ability defined"]))
    available_gadgets = GADGETS_BY_CLASS.get(player_class, [])
    if len(available_gadgets) < 3:
        selected_gadgets = available_gadgets  # fallback if you haven't filled enough yet
    else:
        selected_gadgets = random.sample(available_gadgets, 3)
    return {
        "class": player_class,
        "weapon": weapon,
        "ability": ability,
        "gadgets": selected_gadgets
    }
@bot.command(name="loadout", aliases=["random", "roll"])
async def random_loadout(ctx):
    """Generates a random loadout for The Finals"""
    loadout = generate_random_loadout()
    embed = discord.Embed(
        title="🎲 Your Random Loadout",
        color=discord.Color.blue(),
        timestamp=ctx.message.created_at)
    embed.add_field(name="Class", value=f"**{loadout['class']}**", inline=False)
    embed.add_field(name="Weapon / Specialty", value=loadout['weapon'], inline=True)
    embed.add_field(name="Ability", value=loadout['ability'], inline=True)
    embed.add_field(
        name="Gadgets",
        value="\n".join(f"• {g}" for g in loadout['gadgets']),
        inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.display_name} | {loadout['class']} class")
    await ctx.send(embed=embed)
@bot.command(name="light")
async def random_light(ctx):
    """Quick random Light loadout"""
    loadout = generate_random_loadout()
    while loadout["class"] != "Light":
        loadout = generate_random_loadout()
    embed = discord.Embed(title="🎲 Random Light Loadout", color=discord.Color.green())
    embed.add_field(name="Class", value="**Light**", inline=False)
    embed.add_field(name="Weapon", value=loadout["weapon"], inline=True)
    embed.add_field(name="Ability", value=loadout["ability"], inline=True)
    embed.add_field(name="Gadgets", value="\n".join(f"• {g}" for g in loadout["gadgets"]), inline=False)
    await ctx.send(embed=embed)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
if __name__ == "__main__":
    webserver.keep_alive()
    bot.run(token)
