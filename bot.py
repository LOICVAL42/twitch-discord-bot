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
    guild_id = message.guild.id
    prefix = setload.read_value_in_guild(guild_id, "prefix")
    cmd = message.content.split(" ")
    if cmd[0] != prefix:
        return
    if len(cmd) == 1 or cmd[1] == "aide":
        embed = discord.Embed()
        embed.add_field(name="Aide",
                        value="`defPrefixe` - Permet de définir un nouveau "
                        "préfixe pour le bot.\n"
                        "`defSalonTwitch` - Définit le salon ou seront envoyés "
                        "les notifications relatives à Twitch.\n"
                        "`ajoutStreamer` - Rajoute un streamer à la liste de "
                        "ceux qui sont suivis.\n"
                        "`retraitStreamer` - Enlève un streamer de ceux qui "
                        "sont suivis.\n"
                        "`debutNotifsTwitch` - Active les notifications "
                        "venant de Twitch.\n"
                        "`arretNotifsTwitch` - Arrête les notifications venant "
                        "de Twitch")
        await message.channel.send(embed=embed)
        return
    '''
    Change default channel for twitch notifications
    '''
    if cmd[1] == "defSalonTwitch" or cmd[1] == "dST":
        if len(cmd) != 3:
            await message.channel.send("Mauvais format de commande.",
                                 reference=message, mention_author=False)
            return
        channel = message.channel_mentions[0]
        setload.set_value_in_guild(guild_id, "twitchChannel", channel.id)
        await message.channel.send("Salon de notifications Twitch défini dans "
                             f"le salon suivant : {channel.name}",
                             reference=message, mention_author=False)
        return
    '''
    Change prefix used by the bot
    '''
    if cmd[1] == "defPrefixe" or cmd[1] == "dP":
        if len(cmd) != 3:
            await message.channel.send("Mauvais format de commande.",
                                       reference=message, mention_author=False)
            return
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Vous n'avez pas les permissions.",
                                       reference=message, mention_author = False)
            return
        new_prefix = cmd[2]
        if new_prefix.find(" ") != -1:
            await message.channel.send("Le nouveau préfixe ne peut **pas** "
                                       "contenir d'espaces.", reference=message,
                                       mention_author=False)
        setload.set_value_in_guild(guild_id, "prefix", new_prefix)
        await message.channel.send(f"Nouveau préfixe défini : {new_prefix}",
                                   reference=message, mention_author=False)
        return
    '''
    Add streamer to watched streamers
    '''
    if cmd[1] == "ajoutStreamer" or cmd[1] == "aS":
        if len(cmd) != 3:
            await message.channel.send("Mauvais format de commande.",
                                       reference=message, mention_author=False)
            return
        if not os.path.exists(f"guilds_data/{guild_id}/streamers"):
            streamers = []
        else:
            streamers = setload.read_list_in_guild(guild_id, "streamers")
        streamers.append(cmd[2].lower())
        setload.set_value_in_guild(guild_id, "streamers", streamers)
        stream = os.popen(f"twitch api get users -q login={cmd[2]}")
        json_f = stream.read()
        stream.close()
        raw_data = json.loads(json_f)
        data = raw_data["data"][0]
        setload.set_value_in_guild(guild_id, f"{cmd[2].lower()}_image", data["profile_image_url"])
        if setload.read_value_in_guild(guild_id, "monitoringTwitch") == "True":
            await monitoringTwitch.start_monitoring_streamers(message, [cmd[2]])
        await message.channel.send("Nouveau streamer rajouté aux streamers "
                                   f"suivis, {cmd[2]} a été rajouté.",
                                   reference=message, mention_author=False)
        return
    '''
    Remove streamer from watched streamers
    '''
    if cmd[1] == "retraitStreamer" or cmd[1] == "rS":
        if len(cmd) != 3:
            await message.channel.send("Mauvais format de commande.",
                                       reference=message, mention_author=False)
            return
        if not os.path.exists(f"guilds_data/{guild_id}/streamers"):
            await message.channel.send("Aucun streamer n'est suivi.",
                                       reference=message, mention_author=False)
            return
        streamers = setload.read_list_in_guild(guild_id, "streamers")
        if cmd[2] not in streamers:
            await message.channel.send(f"{cmd[2]} n'est déjà pas suivi",
                                       reference=message, mention_author=False)
            return
        streamers.remove(cmd[2])
        setload.set_value_in_guild(guild_id, "streamers", streamers)
        if setload.read_value_in_guild(guild_id, "monitoringTwitch") == "True":
            monitoringTwitch.stop_monitoring_streamer(monitoringTwitch.find_twitch_channel(message.guild),
                                                      cmd[2])
        await message.channel.send(f"{cmd[2]} a bien été retiré de la liste"
                                   " des streameurs suivis.", reference=message,
                                   mention_author=False)
        return
    '''
    Starts monitoring streamers
    '''
    if cmd[1] == "debutNotifsTwitch" or cmd[1] == "dNT":
        if len(cmd) != 2:
            await message.channel.send("Mauvais format de commande.",
                                       reference=message, mention_author=False)
            return
        setload.set_value_in_guild(guild_id, "monitoringTwitch", "True")
        await monitoringTwitch.start_monitoring_streamers(message,
                                                    setload.read_list_in_guild(
                                                        guild_id, "streamers"))
        await message.channel.send("Activation du suivi des streamers.",
                                   reference=message, mention_author=True)
        return
    '''
    Stops monitoring streamers
    '''
    if cmd[1] == "arretNotifsTwitch" or cmd[1] == "aNT":
        if len(cmd) != 2:
            await message.channel.send("Mauvais format de commande.",
                                       reference=message, mention_author=False)
            return
        setload.set_value_in_guild(guild_id, "monitoringTwitch", "False")
        monitoringTwitch.stop_monitoring_streamers(monitoringTwitch.find_twitch_channel(message.guild),
                                                   setload.read_list_in_guild(guild.id, "streamers"))
        await message.channel.send("Désactivation du suivi des streamers.",
                                   reference=message, mention_author=True)
        return
    '''
    Stops the bot
    '''
    if cmd[1] == "arretBot" or cmd[1] == "aB":
        if len(cmd) != 2:
            await message.channel.send("Mauvais format de commande.",
                                       reference=message, mention_author=False)
            return
        if message.author.id != 275295502168358913:
            await message.channel.send("Vous n'avez pas cette permission.",
                                       reference=message, mention_author=False)
            return
        monitoringTwitch.stop_monitoring_all_streamers()
        await client.close()
        return
    '''
    Test function for embed messages
    '''
    if cmd[1] == "testEmbed" or cmd[1] == "tE":
        if len(cmd) != 2:
            await message.channel.send("Mauvais format de commande.",
                                       reference=message, mention_author=False)
            return
        embed=discord.Embed(title="Title",type="rich",description="description",
                            url="https://www.google.fr/",colour=154)
        await message.channel.send(embed=embed)
        return

monitoringTwitch.monitoring.start()
client.run(TOKEN)
print("Bot éteint avec succès. Bonne nuit.")
