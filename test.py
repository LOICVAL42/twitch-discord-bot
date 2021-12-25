import os
import json
import time
import setload

def IsLive(is_live):
    print("cc")
    stream = os.popen("twitch api get streams -q user_login=emilio_0")
    json_f = stream.read()
    stream.close()
    raw_data = json.loads(json_f)
    print(len(raw_data["data"]))
    if len(raw_data["data"]) == 0:
        is_live = False
    elif not is_live:
        print("Utilisateur en live !")
        is_live = True
    return is_live

def main():
    is_live = False
    while True:
        is_live = IsLive(is_live)
        time.sleep(5)

setload.set_value_in_guild(1, "test", ["1", "2", "3", "4", "5"])
print(setload.read_list_in_guild(1, "test"))
print([i for i in range(15)])
setload.set_value_in_guild(1, "test2", [i for i in range(15)])
print(setload.read_int_list_in_guild(1, "test2"))
