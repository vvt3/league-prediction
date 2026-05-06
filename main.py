import json
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ["*"] for public APIs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Draft(BaseModel):
    team1: list[str]
    team2: list[str]


@app.post("/analyse")
def analyze(draft: Draft):
    return predict(draft.team1, draft.team2)


# Load Champion Data
with open("champions.json") as f:
    CHAMPS = json.load(f)

CC_QUANIFIED = {
    "stun": 5,
    "slow": 1,
    "knockup": 3,
    "root": 2,
    "silence": 1,
    "suppress": 4,
    "ground": 1,
    "taunt": 1,
    "fear": 3,
    "sleep": 4,
    "pull": 3,
    "blind": 1,
    "charm": 3,
    "airborne": 4,
    "polymorph": 5,
    "disarm": 2,
}

HARD_CC = {"stun", "knockup", "sleep", "suppress", "polymorph", "taunt", "fear"}
MID_CC = {"root", "pull", "charm", "airborne", "disarm"}
SOFT_CC = {"slow", "silence", "blind", "ground"}

ROLES_QUANTIFIED = {
    "tank": 3,
    "fighter": 3,
    "mage": 4,
    "marksman": 5,
    "assassin": 3,
    "support": 1,
}


def get_scaling(tags):
    if "marksman" in tags:
        return 5
    if "mage" in tags:
        return 4
    if "fighter" in tags:
        return 3
    return 2


# Team Analysis
def analyse_team(champs):
    team = {
        "ad": 0,
        "ap": 0,
        "damagePotential": 0,
        "cc": 0,
        "hardCC": 0,
        "midCC": 0,
        "softCC": 0,
        "tank": 0,
        "roleScore": 0,
        "compPhysical": 0,
        "compMagic": 0,
    }

    for champ in champs:
        c = CHAMPS[champ]
        cc_score = 0
        role_score = 0
        hard = 0
        mid = 0
        soft = 0

        team["ad"] += c["attack"]
        team["ap"] += c["magic"]
        team["tank"] += c["playstyleInfo"]["durability"] + c["defense"]
        if "tank" in c["roles"]:
            team["tank"] += 3

        # CC Scoring
        team["cc"] += c["playstyleInfo"]["crowdControl"] * 2

        for effect in c["statusEffects"]:
            cc_score += CC_QUANIFIED.get(effect, 0)
            if effect in HARD_CC:
                hard += 3
            elif effect in MID_CC:
                mid += 2
            elif effect in SOFT_CC:
                soft += 1

        team["cc"] += cc_score
        team["hardCC"] += hard
        team["midCC"] += mid
        team["softCC"] += soft

        for role in c["roles"]:
            role_score += ROLES_QUANTIFIED.get(role.lower(), 0)

        team["roleScore"] = team.get("roleScore", 0) + role_score

        if c["damage type"] == "kPhysical":
            team["compPhysical"] += 1
        elif c["damage type"] == "kMagic":
            team["compMagic"] += 1

        team["damagePotential"] = (
            c["attack"] * 0.6 + c["magic"] * 0.6 + c["playstyleInfo"]["damage"] * 1.5
        )

    return team


# Helper Functions
def calcEngage(t1, t2, score, reasons):
    if t1["cc"] > t2["cc"]:
        if t1["tank"] > 9:  # rough engage proxy
            score += 0.3
            reasons.append("Strong CC with frontline to apply it")
        else:
            score += 0.1
            reasons.append("Higher CC but limited engage")

    if t1["tank"] < 8:
        score -= 0.2
        reasons.append("No reliable frontline")

    return score, reasons


def calcCC(t1, t2, score, reasons):
    if t1["cc"] > t2["cc"]:
        score += 0.1
        reasons.append("Higher overall CC potential")

    if t1["hardCC"] > t2["hardCC"]:
        score += 0.25
        reasons.append("Stronger lockdown potential")

    return score, reasons


def calcSampleComps(t1, t2, score, reasons):
    # Front-to-Back Comp
    if t1["tank"] > 10 and t1["cc"] > 3:
        score += 0.2
        reasons.append("Strong front-to-back teamfight comp")

    # Glass Cannon Comp
    if t1["tank"] < 6 and t1["ad"] + t1["ap"] > 40:
        score += 0.1
        reasons.append("High damage but fragile composition")

    # Team Comparisons
    # Tank vs no tank
    if t1["tank"] > 10 and t2["tank"] < 8:
        score += 0.2
        reasons.append("Enemy lacks frontline to match yours")

    # CC vs squishy
    if t1["cc"] > 3 and t2["tank"] < 8:
        score += 0.2
        reasons.append("Enemy vulnerable to CC chain")

    return score, reasons


def calcDmgBreakdown(t1, t2, score, reasons):
    damageAdvantage = (t1["ad"] + t1["ap"]) - (t2["ad"] + t2["ap"])

    if damageAdvantage > 5:
        score += 0.3
        reasons.append("Higher overall damage output")

    phys_ratio = t1["compPhysical"] / 5
    magic_ratio = t1["compMagic"] / 5

    phys_ratio_t2 = t2["compPhysical"] / 5
    magic_ratio_t2 = t2["compMagic"] / 5

    if phys_ratio > 0.8 or magic_ratio > 0.8:
        score -= 0.3
        reasons.append("Highly skewed damage (easy to itemise against)")
    elif phys_ratio > 0.7 or magic_ratio > 0.7:
        score -= 0.2
        reasons.append("Slightly unbalanced damage")
    elif phys_ratio_t2 > 0.7 or magic_ratio_t2 > 0.7:
        score += 0.2
        reasons.append("Enemy team has slightly unbalanced damage")

    print(
        "Team 1s damage potential is:",
        t1["damagePotential"],
        "\nTeam 2s damage potential is: ",
        t2["damagePotential"],
    )

    return score, reasons


# Comparison Logic
def compare(t1, t2):
    score = 0
    reasons = []

    score, reasons = calcEngage(t1, t2, score, reasons)
    score, reasons = calcSampleComps(t1, t2, score, reasons)
    score, reasons = calcDmgBreakdown(t1, t2, score, reasons)
    score, reasons = calcCC(t1, t2, score, reasons)

    return score, reasons


# Sigmoid
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# Prediction
def predict(team1, team2):
    t1 = analyse_team(team1)
    t2 = analyse_team(team2)

    score, reasons = compare(t1, t2)

    return {"winProbability": round(sigmoid(score * 3), 2), "reasons": reasons[:3]}


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
    team1 = ["Ornn", "Kindred", "Lux", "Jhin", "Lulu"]
    team2 = ["Darius", "Talon", "Orianna", "Twitch", "Nami"]
    # team2 = ["Yuumi", "Yuumi", "Yuumi", "Yuumi", "Yuumi"]

    result = predict(team1, team2)

    print("Composition Overview:")
    for r in result["reasons"]:
        print("-> ", r)
    print(f"Your chance of a Win is {result['winProbability'] * 100:.0f}%")

    # TESTING
    t1 = analyse_team(team1)
    t2 = analyse_team(team2)
