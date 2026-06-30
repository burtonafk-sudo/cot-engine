import requests
import pandas as pd
import json

OUTPUT_FILE = "cot.json"

# CFTC Legacy dataset (Socrata API endpoint)
URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# mapping futures → CFTC commodity names (musíš doladiť podľa datasetu)
SYMBOL_MAP = {
    "ES": "E-MINI S&P 500 STOCK INDEX - CME",
    "CL": "CRUDE OIL, LIGHT SWEET - NYMEX",
    "DX": "U.S. DOLLAR INDEX - ICE"
}

def fetch_data():
    r = requests.get(URL)
    data = r.json()
    return pd.DataFrame(data)

def get_latest(df, name):
    sub = df[df["contract_market_name"] == name]
    sub = sub.sort_values("report_date_as_yyyy_mm_dd")
    return sub.iloc[-1]

def build_cot(df):
    out = {}

    for symbol, name in SYMBOL_MAP.items():
        try:
            row = get_latest(df, name)

            commercial_long = int(row["commercial_long_all"])
            commercial_short = int(row["commercial_short_all"])

            out[symbol] = {
                "commercial_long": commercial_long,
                "commercial_short": commercial_short,
                "commercial_net": commercial_long - commercial_short
            }

        except Exception as e:
            out[symbol] = {
                "error": str(e)
            }

    return out

if __name__ == "__main__":
    df = fetch_data()
    cot = build_cot(df)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(cot, f, indent=2)

    print("COT updated (real data)")
