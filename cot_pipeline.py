import json
import requests

# =========================
# CONFIG (môžeš upraviť)
# =========================
OUTPUT_FILE = "cot.json"

# =========================
# SAMPLE STRUCTURE (ES, CL, DX)
# neskôr sem napojíš CFTC parsing
# =========================
data = {
    "ES": {
        "commercial_long": 0,
        "commercial_short": 0,
        "commercial_net": 0
    },
    "CL": {
        "commercial_long": 0,
        "commercial_short": 0,
        "commercial_net": 0
    },
    "DX": {
        "commercial_long": 0,
        "commercial_short": 0,
        "commercial_net": 0
    }
}

# =========================
# PLACEHOLDER FOR CFTC LOGIC
# sem budeš neskôr napájať API / CSV parsing
# =========================
def fetch_and_update():
    # TODO: sem vložíš reálne CFTC parsing
    # teraz len test data aby pipeline fungovala
    data["ES"]["commercial_long"] = 120000
    data["ES"]["commercial_short"] = 90000
    data["ES"]["commercial_net"] = 30000

    data["CL"]["commercial_long"] = 200000
    data["CL"]["commercial_short"] = 210000
    data["CL"]["commercial_net"] = -10000

    data["DX"]["commercial_long"] = 40000
    data["DX"]["commercial_short"] = 35000
    data["DX"]["commercial_net"] = 5000


def save_json():
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    fetch_and_update()
    save_json()
    print("cot.json generated successfully")
