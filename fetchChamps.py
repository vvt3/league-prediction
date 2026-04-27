import requests
import json

VERSION = "14.7.1"  # TODO get from riot
BASE_URL = f"https://ddragon.leagueoflegends.com/cdn/{VERSION}/data/en_US"

# Get all champions
champion_list_url = f"{BASE_URL}/champion.json"
champion_list = requests.get(champion_list_url).json()["data"]

all_champs = {}

for champ_name in champion_list:
    champ_url = f"{BASE_URL}/champion/{champ_name}.json"
    champ_data = requests.get(champ_url).json()["data"][champ_name]
    all_champs[champ_name] = champ_data
    print("Fetching:", champ_name)

# Save raw data
with open("raw_champions.json", "w") as f:
    json.dump(all_champs, f, indent=2)

print("Saved raw_champions.json")
