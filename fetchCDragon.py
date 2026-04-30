import requests
import json

BASE_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/"

# champion ids
champions = {}

for champ_id in range(1, 1000):
    url = f"{BASE_URL}{champ_id}.json"

    try:
        res = requests.get(url)
        if res.status_code != 200:
            continue

        data = res.json()

        name = data.get("alias") or data.get("name")
        if not name:
            continue

        champions[name] = data

        print(f"Fetched {name}")

    except Exception:
        print(Exception)
        continue


with open("community_champions.json", "w") as f:
    json.dump(champions, f, indent=2)

print("Saved community_champions.json")
