import os
import sys
import requests
import asyncio
import time
import discord
import json
from dotenv import load_dotenv
import setload
from multiprocessing import Process
import monitoringTwitch
from discord.ext import tasks
import random
import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} s\'est connecté à Discord !')
    for guild in client.guilds:
        if setload.read_value_in_guild(guild.id, "monitoringTwitch") == "True":
            await monitoringTwitch.start_monitoring_streamers_on_ready(guild,
                            setload.read_list_in_guild(guild.id, "streamers"))

@client.event
async def on_guild_join(guild):
    print(f"{client.user} a rejoint {guild.name} !")
    if os.path.isdir(f"guilds_data/{guild.id}"):
        if not os.path.exists(f"guilds_data/{guild.id}/prefix"):
            setload.set_value_in_guild(guild.id, "prefix", "E!")
        return
    setload.add_guild(guild.id)
    return

async def on_guild_remove(guild):
    set_value_in_guild(guild.id, "monitoringTwitch", "False")
    return


@client.event
async def on_message(message):
    prefix = setload.read_value_in_guild(message.guild.id, "prefix")
    cmd = message.content.split(" ")
    if cmd[0] != prefix:
        return
    if len(cmd) == 1 or cmd[1] == "aide":
        await commands.help_message(message, cmd)
        return
    if cmd[1] == "defSalonTwitch" or cmd[1] == "dST":
        await commands.define_twitch_channel(message, cmd)
        return
    if cmd[1] == "defPrefixe" or cmd[1] == "dP":
        await commands.change_prefix(message, cmd)
        return
    if cmd[1] == "ajoutStreamer" or cmd[1] == "aS":
        await commands.add_streamer(message, cmd)
        return
    if cmd[1] == "retraitStreamer" or cmd[1] == "rS":
        await commands.remove_streamer(message, cmd)
        return
    if cmd[1] == "debutNotifsTwitch" or cmd[1] == "dNT":
        await commands.start_monitoring(message, cmd)
        return
    if cmd[1] == "arretNotifsTwitch" or cmd[1] == "aNT":
        await commands.stop_monitoring(message, cmd)
        return
    if cmd[1] == "arretBot" or cmd[1] == "aB":
        if message.author.id != 275295502168358913:
            await message.channel.send("Vous n'avez pas cette permission.",
                                       reference=message, mention_author=False)
            return
        await commands.stop_bot(message, cmd)
        return

if not os.path.exists("client_infos"):
    os.system("mkdir client_infos")
if not os.path.exists("guilds_data"):
    os.system("mkdir guilds_data")
os.system("python monitoringTwitch.py")
filecid = open("client_infos/client_id")
fileauth = open("client_infos/auth")
filecid.close()
fileauth.close()
monitoringTwitch.monitoring.start()
client.run(TOKEN)
print("Bot éteint avec succès. Bonne nuit.")
