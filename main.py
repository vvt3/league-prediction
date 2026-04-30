import json
import math

# Load Champion Data
with open("champions.json") as f:
    CHAMPS = json.load(f)

CC_QUANIFIED = {
    "stun": 5,
    "slow": 1,
    "knockup": 3,
    "root": 2,
    "silence": 1,
    "supress": 4,
    "ground": 1,
    "flee": 1,
    "taunt": 1,
    "fear": 3,
    "sleep": 4,
    "pull": 3,
    "blind": 1,
    "charm": 3,
    "airbourne": 4,
    "polymorph": 5,
    "disarm": 2,
}


# Team Analysis
def analyse_team(champs):
    team = {
        "ad": 0,
        "ap": 0,
        "cc": 0,
        "tank": 0,
        "engage": 0,
        "scaling": 0,
        "compPhysical": 0,
        "compMagic": 0,
    }

    for champ in champs:
        c = CHAMPS[champ]

        team["ad"] += c["attack"]
        team["ap"] += c["magic"]
        team["tank"] += c["playstyleInfo"]["durability"] + c["defense"]
        team["cc"] += c["playstyleInfo"]["crowdControl"]
        if c["damage type"] == "kPhysical":
            team["compPhysical"] += 1
        elif c["damage type"] == "kMagic":
            team["compMagic"] += 1
        # team["engage"] += c["engage"]
        # team["scaling"] += c["scaling"]

    return team


# Comparison Logic
def compare(t1, t2):
    score = 0
    reasons = []

    if t1["cc"] > t2["cc"]:
        if t1["tank"] > 20:  # rough engage proxy
            score += 0.3
            reasons.append("Strong CC with frontline to apply it")
        else:
            score += 0.1
            reasons.append("Higher CC but limited engage")

    if t1["tank"] < 15:
        score -= 0.2
        reasons.append("No reliable frontline")

    # Front-to-Back Comp
    if t1["tank"] > 20 and t1["cc"] > 15:
        score += 0.2
        reasons.append("Strong front-to-back teamfight comp")

    # Glass Cannon Comp
    if t1["tank"] < 12 and t1["ad"] + t1["ap"] > 40:
        score += 0.1
        reasons.append("High damage but fragile composition")

    # Team Comparisons
    # Tank vs no tank
    if t1["tank"] > 20 and t2["tank"] < 15:
        score += 0.2
        reasons.append("Enemy lacks frontline to match yours")

    # CC vs squishy
    if t1["cc"] > 15 and t2["tank"] < 15:
        score += 0.2
        reasons.append("Enemy vulnerable to CC chain")

    damage_advantage = (t1["ad"] + t1["ap"]) - (t2["ad"] + t2["ap"])

    if damage_advantage > 5:
        score += 0.2
        reasons.append("Higher overall damage output")

    phys_ratio = t1["compPhysical"] / 5
    magic_ratio = t1["compMagic"] / 5

    if phys_ratio > 0.8 or magic_ratio > 0.8:
        score -= 0.3
        reasons.append("Highly skewed damage (easy to itemise against)")
    elif phys_ratio > 0.6 or magic_ratio > 0.6:
        score -= 0.1
        reasons.append("Slightly unbalanced damage")

    return score, reasons


# Sigmoid
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# Prediction
def predict(team1, team2):
    t1 = analyse_team(team1)
    t2 = analyse_team(team2)

    score, reasons = compare(t1, t2)

    return {"winProbability": round(sigmoid(score), 2), "reasons": reasons[:3]}


# Champion Tags
def getTags(champs):
    tags = []
    for champ in champs:
        c = CHAMPS[champ]
        for tag in c["roles"]:
            tags.append(tag)

    return set(tags)


CHAMPIONLIST = []
for c in CHAMPS:
    CHAMPIONLIST.append(c)

ROLELIST = getTags(CHAMPIONLIST)

# Test
if __name__ == "__main__":
    team1 = ["Yuumi", "Yuumi", "Yuumi", "Yuumi", "Yuumi"]
    team2 = ["Darius", "Sejuani", "Lux", "Twitch", "Nami"]

    result = predict(team1, team2)

    print(f"Team 1s chance of a Win is {result['winProbability'] * 100:.0f}%")
    print("Composition Overview:")
    for r in result["reasons"]:
        print("-> ", r)
