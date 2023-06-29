import os
import discord

from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TOKEN')
print(TOKEN)
from discord.ext import commands
from discord import app_commands

import openaibit

# Loading LLM bit
queryboy = openaibit.warming_llm_engine()

# Setting Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='$$',intents=intents)

# Creating static lists of media and stinky global variables for the bot to play around with
fileList = os.listdir("media_files")
print(f"Here's what's in the media files right now: {fileList}")
bot.cmdsList = []


# Setting bot events
@bot.event
async def on_ready():
    print("Ready?")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        rawCmdList:AppCommand = await bot.tree.fetch_commands()
        bot.cmdsList = [i.name for i in rawCmdList]
    except Exception as e:
        print(e)

# Setting bot commands
# Note: Remember that anything that requires sending large media files (.mp3, .mp4, etc.) will require a ctx.await()

@bot.hybrid_command(name="sendmedia", description="Sends a media file a certain amount of times, kinda of media specified in the command.")
async def sendmedia(ctx, media:str, quantity:int):
    quantity = int(quantity)
    await ctx.defer()
    if media in fileList:
        for i in range(quantity):
            await ctx.send(file=discord.File(f'media_files/{media}'))

@bot.hybrid_command(name="listsmartcmds", description="Gives a list of commands that are currently in this bot's database.")
async def listsmartcmds(ctx):
    await ctx.send(file=discord.File('text_data/cmds.txt'))


@bot.hybrid_command(name="pingu", description="Mentions a user a set amount of times.")
async def pingu(ctx, name:str, quantity:int):
    quantity = int(quantity)
    await ctx.defer()
    for i in range(quantity):
        await ctx.send(f"# Hello {name} Hello {name}")

# This is the smart command accessing command, which will take in a query and filter that into one of the hybrid cmds
@bot.tree.command(name="outputex", description="Takes a verbose text input and interprets it as an existing bot command if possible")
@app_commands.describe(gimme = "A verbose text input that somewhat corresponds to a function in the commands list")
async def outputex(interaction: discord.Interaction, gimme: str):
    # Query the person's statement
    cmdAttempt = queryboy.query(f"The data is a reference sheet for commands. What command does the statement '{gimme}' most resemble in format or description? Try and match based on high similarity in keywords too. The command description is on the same line as the command format, but after the ':'. Do not include anything after the colon in response, make it match the command as closely as possible. If amounts/numbers are mentioned as a relevant argument, get the number equivalent and replace the relevant [int](s) with it. If a string similar to '<@191348840098562052>' is present and [name] is in the command, replace [name] with it. Do not leave any square brackets.")
    cmdCleaned = str(cmdAttempt).strip()

    # Format chatGPT's response in a proper command that could be read as a prefix command
    cmdSplit = cmdCleaned.split(" ")
    print(cmdSplit)
    ctx = await bot.get_context(interaction)

    # Handle cmds
    # retrieve list from commands list and base validity off of that. If the firs.t of the list is in the cmdlist, then use it to get_command.
    # fill out the command function with ctx, then the unpacked cmdSplit as args.
    print(f"Checking if {cmdSplit[0]} is in {bot.cmdsList}")
    if cmdSplit[0] in bot.cmdsList:
        command = bot.get_command(str(cmdSplit[0]))
        await command(ctx, *cmdSplit[1:])
    else:
        await interaction.response.send_message("Tbh I can't be arsed to parse through what you just posted")

    try:
        await interaction.channel.send("We're done here.",delete_after=3)
        # Flavor text for the user to look at and go 'oooohh and aaaaaahh'
        await interaction.channel.send(
            f"__Check this out!__\nI got this as your input: {gimme}\nAnd through some LLM stuff I was able to parse it into this: {cmdCleaned}\nCool, huh? 😎")
    except:
        print("we ain't getting out of the hood")

bot.run(TOKEN)