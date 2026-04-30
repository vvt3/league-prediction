import json
import re

NORMALISE = {
    "Stun": "stun",
    "Stuns": "stun",
    "Stunned": "stun",
    "Stunning": "stun",
    "Slow": "slow",
    "Slows": "slow",
    "Slowed": "slow",
    "slows": "slow",
    "Slowing": "slow",
    "Knock Up": "knockup",
    "Knocks Up": "knockup",
    "Knocked Up": "knockup",
    "Knocking Up": "knockup",
    "Knock Back": "knock",
    "Knocks Back": "knock",
    "Knocked Back": "knock",
    "Knocking Back": "knock",
    "Knocked": "knock",
    "Knocks": "knock",
    "Knock": "knock",
    "Knocking": "knockup",
    "Knock Aside": "knock",
    "Knocked Away": "knock",
    "Knocking Away": "knock",
    "Root": "root",
    "Roots": "root",
    "Rooted": "root",
    "Rooting": "root",
    "Silence": "silence",
    "Silenced": "silence",
    "Silences": "silence",
    "Silencing": "silence",
    "Suppress": "supress",
    "Suppressing": "supress",
    "Suppressed": "supress",
    "Suppresses": "supress",
    "Grounding": "ground",
    "Grounded": "ground",
    "Flee": "flee",
    "Taunting": "taunt",
    "Taunts": "taunt",
    "Fear": "fear",
    "Fears": "fear",
    "Fearing": "fear",
    "Feared": "fear",
    "Drowsy": "sleep",
    "Asleep": "sleep",
    "Pull": "pull",
    "Pulls": "pull",
    "Pulled": "pull",
    "Pushing": "pull",
    "Pulls In": "pull",
    "Drags": "pull",
    "Dragging": "pull",
    "Blinding": "blind",
    "Charms": "charm",
    "Airbourne": "airbourne",
    "Polymorphs": "polymorph",
    "Disarmed": "disarm",
    "Disabling": "disarm",
    "Immobilized": "immobile",
    "Immobilizing": "immobile",
    "Immobilizes": "immobile",
}

VALID_STATUS = (
    "stun",
    "slow",
    "knockup",
    "root",
    "silence",
    "supress",
    "ground",
    "flee",
    "taunt",
    "fear",
    "sleep",
    "pull",
    "blind",
    "charm",
    "airbourne",
    "polymorph",
    "disarm",
)

with open("raw_champions.json") as f:
    rawRiot = json.load(f)

with open("community_champions.json") as f:
    rawComminity = json.load(f)

cleaned = {}


def normaliseStatus(effects):
    data = []
    for effect in effects:
        effect = effect.lower().strip()
        if "stun" in effect:
            data.append("stun")
        elif "slow" in effect:
            data.append("slow")
        elif "root" in effect:
            data.append("root")
        elif "knock" in effect:
            data.append("knock")
        elif "silenc" in effect:
            data.append("silence")
        elif "fear" in effect:
            data.append("fear")
        elif "taunt" in effect:
            data.append("taunt")
        elif "flee" in effect:
            data.append("flee")
        elif "ground" in effect:
            data.append("ground")
        elif "disarm" in effect:
            data.append("disarm")
        elif "polymorph" in effect:
            data.append("polymorph")
        elif "airbourne" in effect:
            data.append("airbourne")
        elif "charm" in effect:
            data.append("charm")
        elif "supress" in effect:
            data.append("supress")
        elif "blind" in effect:
            data.append("blind")
        elif "pull" in effect:
            data.append("pull")
        elif "sleep" in effect:
            data.append("sleep")

    return data


def getStatusTags(spellInfo):
    status = []
    tooltips = []
    # Get Tooltips
    for info in spellInfo:
        tooltips.append(info["tooltip"])
    # Get <status>
    for t in tooltips:
        matches = re.findall(r"<status>(.*?)</status>", t)
        if matches:
            result = [m.strip() for m in matches]
            status.append(result)
    flat = [tag for tags in status for tag in tags]

    statusNorm = normaliseStatus(flat)

    return statusNorm


for name, champ in rawRiot.items():
    community_champ = rawComminity.get(name)

    cleaned[name] = {
        "roles": champ.get("tags", []),
        "attack": champ["info"]["attack"],
        "defense": champ["info"]["defense"],
        "magic": champ["info"]["magic"],
        # "difficulty": champ["info"]["difficulty"],
        "statusEffects": getStatusTags(champ["spells"]),
        # "passiveInfo": champ["passive"]["description"],
    }

    if community_champ:
        # cleaned[name]["passive"] = community_champ.get("passive", {})
        cleaned[name]["roles"] = community_champ.get("roles", [])
        cleaned[name]["damage type"] = community_champ.get("tacticalInfo")["damageType"]
        cleaned[name]["attack type"] = community_champ.get("tacticalInfo", {})[
            "attackType"
        ]
        cleaned[name]["playstyleInfo"] = community_champ.get("playstyleInfo", {})
        cleaned[name]["championTagInfo"] = community_champ.get("championTagInfo", {})

    print("Finished: ", name)

with open("champions.json", "w") as f:
    json.dump(cleaned, f, indent=2)

print("champions.json created")
