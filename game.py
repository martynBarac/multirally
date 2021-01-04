import json

def load_level(level_name):
    """ level name is the filename without file extension """
    with open("levels/" + level_name + ".txt", "r") as file:
        data = file.read()
    return json.loads(data)