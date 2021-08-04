import json

def stringify_list(l:list[dict]) -> list[str]:
    # Takes list of dictionaries and converts them to strings
    return [json.dumps(o) for o in l]

def dictify_list(l:list[list]) -> list[dict]:
    # Takes list of json formated strings and converts them to dictionaries
    return [json.loads(o) for o in l]