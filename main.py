import json
import math

# Load Champion Data
with open("champions.json") as f:
    CHAMPS = json.load(f)

CC_QUANIFIED = {
    "stun": 10,
    "slow": 10,
    "knockup": 10,
    "root": 10,
    "silence": 10,
    "supress": 10,
    "ground": 10,
    "flee": 10,
    "taunt": 10,
    "fear": 10,
    "sleep": 10,
    "pull": 10,
    "blind": 10,
    "charm": 10,
    "airbourne": 10,
    "polymorph": 10,
    "disarm": 10,
}


# Team Analysis
def analyse_team(champs):
    team = {"ad": 0, "ap": 0, "cc": 0, "tank": 0, "engage": 0, "scaling": 0}

    for champ in champs:
        c = CHAMPS[champ]

        team["ad"] += c["attack"]
        team["ap"] += c["magic"]

        # team["cc"] += c["cc"]
        # team["tank"] += c["tank"]
        # team["engage"] += c["engage"]
        # team["scaling"] += c["scaling"]

    return team


# Comparison Logic
def compare(t1, t2):
    score = 0
    reasons = []

    if t1["cc"] > t2["cc"]:
        score += 0.1
        reasons.append("Stronger crowd control")

    if t2["tank"] < 6:
        score += 0.1
        reasons.append("Enemy lacks frontline")

    if t1["engage"] > t2["engage"]:
        score += 0.1
        reasons.append("Better engage")

    if t1["scaling"] > t2["scaling"]:
        score += 0.1
        reasons.append("Better late game scaling")

    # if t1["ad"] == 5 or t1["ap"] == 5:
    #     score -= 0.1
    #     reasons.append("Unbalanced damage profile")
    if t1["ad"] > t2["ad"]:
        score += 0.1
        reasons.append("Stronger Physcial Dmg")

    if t1["ap"] > t2["ap"]:
        score += 0.1
        reasons.append("Stronger Magic Dmg")

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
        for tag in c["tags"]:
            tags.append(tag)

    return set(tags)


def runThroughChamps(champs):
    for c in champs:
        print(f"{c} Difficulty is: {CHAMPS[c]['difficulty']}")


CHAMPIONLIST = []
for c in CHAMPS:
    CHAMPIONLIST.append(c)

ROLELIST = getTags(CHAMPIONLIST)

# Test
if __name__ == "__main__":
    team1 = ["Quinn", "Kindred", "Varus", "Jinx", "Thresh"]
    team2 = ["Chogath", "Khazix", "Lux", "Twitch", "Nami"]

    result = predict(team1, team2)

    # print(f"Chance of Win is {result['winProbability'] * 100:.0f}%")
    # print("Reasons:")
    # for r in result["reasons"]:
    #     print("-> ", r)

    # runThroughChamps(CHAMPS)
