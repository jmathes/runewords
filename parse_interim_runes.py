import json
from pprint import pprint

with open("interim_runes.txt", "rb") as interim_runes:
    lines = interim_runes.readlines()

runes = []
for line in lines[1:]:
    line = line.decode("utf8").strip().split("\t")
    (name, recipe) = line[:2]
    tail = line[2:]
    level = int(tail[-1]) if tail[-1] != "N/A" else None
    effects = tail[:-1]
    recipe = recipe.strip().split()
    dict_recipe = {
        "rune": {
            "name": recipe[1].split(",")[0],
            "count": int(recipe[0])
        },
        "gem": None,
    }
    if len(recipe) > 2:
        dict_recipe["gem"] = {
            "name": recipe[3].split(",")[0],
            "quality": recipe[2]
        }

    if len(recipe) > 4:
        effects = recipe[4:] + effects

    dict_effects = {
        "weapon": effects[0].split(", "),
        "armor": [],
        "shield": [],
    }
    for effect in effects[1].split(", "):
        if "(shield" in effect:
            dict_effects["shield"].append(effect.split("(")[0])
        else:
            dict_effects["armor"].append(effect)


    runes.append({
        "name": name,
        "recipe": dict_recipe,
        "effects": dict_effects,
        "level": level,
    })

runes = {rune['name']: rune for rune in runes}
runes["El"] = {
    "name": "El",
    "level": 11,
    "recipe": None,
    "effects": {
        "weapon": ["+50 attack rating", "+1 light radius"],
        "armor": ["+15 defense", "+1 light radius"],
        "shield": [],
    }
}
pprint(runes)

with open("runes_by_name.json", "w") as runes_json:
    json.dump(runes, runes_json)

