import json

def stringify_list(l:list[dict]) -> list[str]:
    # Takes list of dictionaries and converts them to strings
    return [json.dumps(o) for o in l]

def dictify_list(l:list[list]) -> list[dict]:
    # Takes list of json formated strings and converts them to dictionaries
    return [json.loads(o) for o in l]

def strip_useless_info(rides:list[dict]) -> list[dict]:
    # Takes raw ride dictionary list from server and
    # strips information that is not used in this script
    # in order to save on memory usage on the system
    return [{"time":ride["occasions"][0]["time"],'location':ride["occasions"][0]["locationName"],'cost':ride["occasions"][0]["cost"],'date':ride["occasions"][0]["date"],'name':ride["occasions"][0]["name"]} for ride in rides]