import os
import discord
import sys

def add_guild(guild_id):
    '''
    Function to add a folder for a guild which has not been generated yet
    '''
    os.mkdir("guilds_data/" + str(guild_id))
    set_value_in_guild(guild_id, "prefix", "E!")
    set_value_in_guild(guild_id, "monitoringTwitch", "False")
    return

def set_value_in_guild(guild_id, value_name, value):
    '''
    Function to set a value for a guild
    '''
    if not os.path.isdir(f"guilds_data/{guild_id}"):
        add_guild(guild_id)
    file = open(f"guilds_data/{guild_id}/{value_name}", "w")
    file.write(str(value))
    file.close()
    return

def read_value_in_guild(guild_id, value_name):
    '''
    Function to read a value from a guild
    '''
    if not os.path.isdir(f"guilds_data/{guild_id}"):
        sys.stderr.write("read_value_in_grid : Dossier de la guilde non trouvé")
        return None
    if not os.path.exists(f"guilds_data/{guild_id}/{value_name}"):
        sys.stderr.write("read_value_in_grid : Fichier de la valeur non trouvé")
        return None
    file = open(f"guilds_data/{guild_id}/{value_name}", "r")
    value = file.read()
    file.close()
    return value

def read_int_in_guild(guild_id, value_name):
    '''
    Reads an int value in a guild
    '''
    raw_value = read_value_in_guild(guild_id, value_name)
    return int(raw_value)

def read_list_in_guild(guild_id, value_name, is_int=False):
    '''
    Reads a list in a guild
    '''
    raw_value = read_value_in_guild(guild_id, value_name)
    if raw_value == '' or raw_value == "[]":
        return []
    if is_int:
        value = raw_value[1:-1].split(", ")
    else:
        value = raw_value[2:-2].split("\', \'")
    return value

def read_int_list_in_guild(guild_id, value_name):
    '''
    Reads a list of int in a guild
    '''
    raw_value = read_list_in_guild(guild_id, value_name, True)
    value = []
    for raw in raw_value:
        value.append(int(raw))
    return value

