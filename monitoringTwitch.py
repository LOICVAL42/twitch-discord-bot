from multiprocessing import Process
import asyncio
import discord
import time
import setload
import os
import json
from discord.ext import tasks
import queue


to_monitor = queue.SimpleQueue()
monitored = []
stop_monitoring = []

@tasks.loop(seconds=10)
async def monitoring():
    global to_monitor
    new_to_monitor = queue.SimpleQueue()
    while not to_monitor.empty():
        (channel, streamer, is_live) = to_monitor.get()
        stream = os.popen(f"twitch api get streams -q user_login={streamer}")
        json_f = stream.read()
        stream.close()
        raw_data = json.loads(json_f)
        if len(raw_data["data"]) == 0:
            is_live = False
        elif not is_live:
            data = raw_data["data"][0]
            embed = discord.Embed(title=data["title"],
                                  url=f"https://www.twitch.tv/{data['user_login']}",
                                  description=f"{data['user_name']} est en live"
                                  f" sur : {data['game_name']} !")
            embed.set_author(name=f"{data['user_name']} est en live !",
                             url=f"https://www.twitch.tv/{data['user_login']}",
                             icon_url=
                             "https://icones.pro/wp-content/uploads/2021/05/symbole-twitch-logo-icone-rose.png")
            embed.set_thumbnail(url=setload.read_value_in_guild(channel.guild.id, f"{streamer}_image"))
            await channel.send("@everyone",embed=embed)
            is_live = True
        if (channel, streamer) not in stop_monitoring:
            new_to_monitor.put((channel, streamer, is_live))
        else:
            stop_monitoring.remove((channel, streamer))
            monitored.remove((channel, streamer))
    to_monitor = new_to_monitor
    return

def find_monitored_streamer(channel, streamer):
    for (mchannel, mstreamer) in monitored:
        if channel == mchannel and streamer == mstreamer:
            return True
    return False

async def start_monitoring_streamer(channel, streamer):
    if find_monitored_streamer(channel.guild.id, streamer):
        return
    to_monitor.put((channel, streamer, False))
    monitored.append((channel, streamer))
    return

async def start_monitoring_streamers_on_ready(guild, streamers):
    channel = find_twitch_channel(guild)
    if channel is None:
        return
    for streamer in streamers:
        await start_monitoring_streamer(channel, streamer)
    return

async def start_monitoring_streamers(message, streamers):
    guild = message.guild
    channel_id = int(setload.read_value_in_guild(guild.id, "twitchChannel"))
    channel = None
    for c in guild.channels:
        if c.id == channel_id:
            channel = c
            break
    if channel is None:
        await message.channel.send("Aucun salon défini pour les notifications "
                             "Twitch. Veuillez utiliser la commande "
                             "\"defSalonTwitch\" pour en définir un.",
                             reference=message, mention_author=False)
        return
    for streamer in streamers:
        await start_monitoring_streamer(channel, streamer)
    return

def stop_monitoring_streamer(channel, streamer):
    if not find_monitored_streamer(channel.guild.id, streamer):
        return
    stop_monitoring.append((channel, streamer))
    return

def stop_monitoring_streamers(channel, streamers):
    for streamer in streamers:
        stop_monitoring_streamer(channel, streamer)

def stop_monitoring_all_streamers():
    monitoring.stop()

def find_twitch_channel(guild):
    channel_id = setload.read_int_in_guild(guild.id, "twitchChannel")
    for c in guild.channels:
        if c.id == channel_id:
            return c
    return None
