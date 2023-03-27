import json
from pprint import pprint
from collections import defaultdict
from copy import deepcopy

with open("runewords.json", "r") as runewords:
    runewords = json.load(runewords)

qualities = [
    "Perfect",
    "Flawless",
    "Normal",
    "Flawed",
    "Chipped",
]


def get_rune_cost(rune, count):
    if runes[rune]["recipe"] is None:
        return count
    return count * get_rune_cost(
        runes[rune]["recipe"]["rune"]["name"],
        runes[rune]["recipe"]["rune"]["count"],
    )

def get_gem_cost(rune, count):
    if runes[rune]["recipe"] is None:
        return 0
    if runes[rune]["recipe"]["gem"] is None:
        return 0
    return count * (
        {
            "Chipped": 1,
            "Flawed": 3,
            "Normal": 9,
            "Flawless": 27,
            "Perfect": 81,
        }[runes[rune]["recipe"]["gem"]["quality"]]
        + get_gem_cost(
            runes[rune]["recipe"]["rune"]["name"],
            runes[rune]["recipe"]["rune"]["count"],
        )
    )

with open("runes_by_name.json", "r") as runes_by_name:
    runes = json.load(runes_by_name)

with open("inventory.json", "r") as inventory:
    inventory = json.load(inventory)
    inventory = {k: (v * 1 if isinstance(v, int) else v) for k, v in inventory.items()}


for word in runewords:
    word["level"] = max([runes[rune]['level'] for rune in word['recipe'] if runes[rune]['level'] is not None])
    word["rune_cost"] = sum(
        get_rune_cost(rune, 1)
        for rune in word["recipe"]
    )
    word["gem_cost"] = sum(
        get_gem_cost(rune, 1)
        for rune in word["recipe"]
    )

def get_class(equipment):
    equipment = equipment.lower()
    if "shield" in equipment:
        return "shield"
    for armor in [
        "armor",
        "helm",
     ]:
        if armor in equipment:
            return "armor"
    for weapon in [
        "club", "hammer", "mace", "weapon", "scept", "stave", "wand", "claw", "axe", "sword", "polearm",
    ]:
        if weapon in equipment:
            return "weapon"
    raise ValueError(f"Cannot classify {equipment}")


def can_afford_gem(gem, quality, count, using, used):
    if count == 0:
        return True, using,
    using = deepcopy(using)
    used = deepcopy(used)
    if using.get(gem, {}).get(quality, 0) >= count:
        using[gem][quality] -= count
        used[gem][quality] += count
        return True, using, used
    elif quality == "Chipped":
        return False, using, used
    else:
        print(using)
        print(gem)
        print(quality)
        count -= using.get(gem, {}).get(quality, 0)
        if gem not in used:
            used[gem] = defaultdict(int)
        used[gem][quality] += using.get(gem, {}).get(quality, 0)
        return can_afford_gem(gem, qualities[qualities.index(quality) + 1], count * 3, using, used)


def can_afford_rune(runes, rune, count, using, used):
    if count == 0:
        return True, using, used
    using = deepcopy(using)
    used = deepcopy(used)
    if using[rune["name"]] >= count:
        using[rune["name"]] -= count
        used[rune["name"]] += count
        return (True, using, used)
    else:
        if rune["recipe"] is None:
            return (False, using, used)
        count -= using[rune["name"]]
        used[rune["name"]] += using[rune["name"]]
        using[rune["name"]] = 0
        can_afford_subrune, using, used = can_afford_rune(
            runes,
            runes[rune["recipe"]["rune"]["name"]],
            count * rune["recipe"]["rune"]["count"],
            using,
            used,
        )
        if not can_afford_subrune:
            return (False, using, used)
        if not rune["recipe"]["gem"]:
            return (True, using, used)
        return can_afford_gem(
            rune["recipe"]["gem"]["name"],
            rune["recipe"]["gem"]["quality"],
            count, using, used)


possibilities = []

for word in runewords:
    spoken_for = defaultdict(int)
    missing = defaultdict(int)
    possible = True
    leftover = deepcopy(inventory)
    used = defaultdict(int)
    for rune in word["recipe"]:
        possible, leftover, used = can_afford_rune(runes, runes[rune], 1, leftover, used)
        if not possible:
            break
    if not possible:
        continue
    possibilities.append((deepcopy(word), deepcopy(used)))


possibilities = sorted(possibilities, key=lambda word: word[0]['level'])

for word, used in possibilities:
    print()
    print(f"{word['name']} ({'+'.join(word['recipe'])}, lvl {word['level']}) [{word['equipment']}]:")
    if any(k > 1 for k in used.values()):
        print(f"  * using {', '.join(str(v) + ' ' + k for k, v in used.items() if v > 0)}")
    prefixes = "\0KMGTP"
    idx = 0
    cost = word['rune_cost']
    while cost > 1000:
        cost = cost/1000
        idx += 1
    cost = int(cost * 10) / 10
    if idx == 0:
        cost = int(cost)
    strcost = f"{cost}{prefixes[idx]} El runes"
    if word['gem_cost'] > 0:
        idx = 0
        cost = word['gem_cost']
        while cost > 1000:
            cost = cost/1000
            idx += 1
        cost = int(cost * 10) / 10
        if idx == 0:
            cost = int(cost)
        strcost += f", {cost}{prefixes[idx]} chipped gems"
    print(f"  Cost: {strcost}")
    for effect in word['effects']:
        print(f"    {effect}")
    item_class = get_class(word["equipment"])
