import json
import math

# Load Champion Data
with open("champions.json") as f:
    CHAMPS = json.load(f)


# Team Analysis
def analyse_team(champs):
    team = {"ad": 0, "ap": 0, "cc": 0, "tank": 0, "engage": 0, "scaling": 0}

    for champ in champs:
        c = CHAMPS[champ]

        if c["damageType"] == "AD":
            team["ad"] += 1
        else:
            team["ap"] += 1

        team["cc"] += c["cc"]
        team["tank"] += c["tank"]
        team["engage"] += c["engage"]
        team["scaling"] += c["scaling"]

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

    if t1["ad"] == 5 or t1["ap"] == 5:
        score -= 0.1
        reasons.append("Unbalanced damage profile")

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


# Test
if __name__ == "__main__":
    team1 = ["Ahri", "LeeSin", "Ornn", "Jinx", "Thresh"]
    team2 = ["Zed", "KhaZix", "Lux", "Ezreal", "Yuumi"]

    result = predict(team1, team2)

    print(f"Win Probability: {result['winProbability'] * 100:.0f}%")
    print("Reasons:")
    for r in result["reasons"]:
        print("-", r)
