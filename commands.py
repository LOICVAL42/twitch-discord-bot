import discord
import os
import requests

import setload
import monitoringTwitch
import permissions

async def help_message(message, cmd):
    '''
    Displays the help message
    '''
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

async def define_twitch_channel(message, cmd):
    '''
    Changes channel for twitch notifications
    '''
    if not permissions.twitch_permissions(message.channel, message.author):
        await permissions.no_permissions_ans(message)
        return
    if len(cmd) != 3:
        await message.channel.send("Mauvais format de commande.",
                             reference=message, mention_author=False)
        return
    channel = message.channel_mentions[0]
    setload.set_value_in_guild(message.guild.id, "twitchChannel", channel.id)
    await message.channel.send("Salon de notifications Twitch défini dans "
                         f"le salon suivant : {channel.name}",
                         reference=message, mention_author=False)

async def change_prefix(message, cmd):
    '''
    Changes the prefix used by the bot
    '''
    if not permissions.bot_permissions(message.channel, message.author):
        await permissions.no_permissions_ans(message)
        return
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
    setload.set_value_in_guild(message.guild.id, "prefix", new_prefix)
    await message.channel.send(f"Nouveau préfixe défini : {new_prefix}",
                               reference=message, mention_author=False)

async def add_streamer(message, cmd):
    '''
    Adds a streamer to monitored streamers
    '''
    if not permissions.twitch_permissions(message.channel, message.author):
        await permissions.no_permissions_ans(message)
        return
    if len(cmd) != 3:
        await message.channel.send("Mauvais format de commande.",
                                   reference=message, mention_author=False)
        return
    if not os.path.exists(f"guilds_data/{message.guild.id}/streamers"):
        streamers = []
    else:
        streamers = setload.read_list_in_guild(message.guild.id, "streamers")
    streamers.append(cmd[2].lower())
    setload.set_value_in_guild(message.guild.id, "streamers", streamers)
    stream = requests.get("https://api.twitch.tv/helix/users?login=" + cmd[2], headers=monitoringTwitch.headers)
    raw_data = stream.json()
    data = raw_data["data"][0]
    setload.set_value_in_guild(message.guild.id, f"{cmd[2].lower()}_image", data["profile_image_url"])
    if setload.read_value_in_guild(message.guild.id, "monitoringTwitch") == "True":
        await monitoringTwitch.start_monitoring_streamers(message, [cmd[2]])
    await message.channel.send("Nouveau streamer rajouté aux streamers "
                               f"suivis, {cmd[2]} a été rajouté.",
                               reference=message, mention_author=False)

async def remove_streamer(message, cmd):
    '''
    Removes a streamer from monitored streamers
    '''
    if not permissions.twitch_permissions(message.channel, message.author):
        await permissions.no_permissions_ans(message)
        return
    if len(cmd) != 3:
        await message.channel.send("Mauvais format de commande.",
                                   reference=message, mention_author=False)
        return
    if not os.path.exists(f"guilds_data/{message.guild.id}/streamers"):
        await message.channel.send("Aucun streamer n'est suivi.",
                                   reference=message, mention_author=False)
        return
    streamers = setload.read_list_in_guild(message.guild.id, "streamers")
    if cmd[2] not in streamers:
        await message.channel.send(f"{cmd[2]} n'est déjà pas suivi",
                                   reference=message, mention_author=False)
        return
    streamers.remove(cmd[2])
    setload.set_value_in_guild(message.guild.id, "streamers", streamers)
    if setload.read_value_in_guild(message.guild.id, "monitoringTwitch") == "True":
        monitoringTwitch.stop_monitoring_streamer(monitoringTwitch.find_twitch_channel(message.guild),
                                                  cmd[2])
    await message.channel.send(f"{cmd[2]} a bien été retiré de la liste"
                               " des streameurs suivis.", reference=message,
                               mention_author=False)

async def start_monitoring(message, cmd):
    '''
    Starts monitoring twitch streamers
    '''
    if not permissions.twitch_permissions(message.channel, message.author):
        await permissions.no_permissions_ans(message)
        return
    if len(cmd) != 2:
        await message.channel.send("Mauvais format de commande.",
                                   reference=message, mention_author=False)
        return
    setload.set_value_in_guild(message.guild.id, "monitoringTwitch", "True")
    await monitoringTwitch.start_monitoring_streamers(message,
                                                setload.read_list_in_guild(
                                                   message.guild.id, "streamers"))
    await message.channel.send("Activation du suivi des streamers.",
                               reference=message, mention_author=True)

async def stop_monitoring(message, cmd):
    '''
    Stops monitoring twitch streamers
    '''
    if not permissions.twitch_permissions(message.channel, message.author):
        await permissions.no_permissions_ans(message)
        return
    if len(cmd) != 2:
        await message.channel.send("Mauvais format de commande.",
                                   reference=message, mention_author=False)
        return
    setload.set_value_in_guild(message.guild.id, "monitoringTwitch", "False")
    monitoringTwitch.stop_monitoring_streamers(monitoringTwitch.find_twitch_channel(message.guild),
                                               setload.read_list_in_guild(message.guild.id, "streamers"))
    await message.channel.send("Désactivation du suivi des streamers.",
                               reference=message, mention_author=True)
