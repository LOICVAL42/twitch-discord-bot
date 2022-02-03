import discord

def bot_permissions(channel, member):
    return channel.permissions_for(member).administrator

def twitch_permissions(channel, member):
    return channel.permissions_for(member).manage_webhooks

async def no_permissions_ans(message):
    await message.channel.send("Vous n'avez pas les permissions pour cette commande.",
                               reference=message, mention_author=False)
