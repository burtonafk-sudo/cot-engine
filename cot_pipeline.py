import requests
import pandas as pd
import json

OUTPUT_FILE = "cot.json"

URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# =========================
# CONFIG – robustné matching namiesto exact stringov
# =========================
SYMBOL_MAP = {
    "ES": ["S&P", "E-MINI", "SP 500"],
    "CL": ["CRUDE OIL", "LIGHT SWEET", "NYMEX"],
    "DX": ["DOLLAR INDEX", "U.S. DOLLAR"]
}

# =========================
# FETCH DATA
# =========================
def fetch_data():
    print("Fetching CFTC data...")

    r = requests.get(URL, timeout=30)

    if r.status_code != 200:
        raise Exception(f"CFTC API error: {r.status_code}")

    data = r.json()

    df = pd.DataFrame(data)

    print("Rows received:", len(df))
    print("Columns:", list(df.columns))

    return df


# =========================
# FIND BEST MATCH ROW
# =========================
def find_latest_match(df, keywords):
    if "contract_market_name" not in df.columns:
        raise Exception("Missing column: contract_market_name")

    mask = df["contract_market_name"].str.upper()

    for kw in keywords:
        mask = mask.str.contains(kw.upper(), na=False) | mask

    filtered = df[mask]

    print(f"Matches found: {len(filtered)} for keywords {keywords}")

    if filtered.empty:
        return None

    # sort by date if exists
    date_col = "report_date_as_yyyy_mm_dd"

    if date_col in filtered.columns:
        filtered = filtered.sort_values(date_col)

    return filtered.iloc[-1]


# =========================
# BUILD COT STRUCTURE
# =========================
def build_cot(df):
    result = {}

    for symbol, keywords in SYMBOL_MAP.items():

        print(f"\nProcessing {symbol}...")

        row = find_latest_match(df, keywords)

        if row is None:
            print(f"WARNING: No data for {symbol}")
            result[symbol] = {
                "error": "no match found"
            }
            continue

        try:
            long = float(row.get("commercial_long_all", 0))
            short = float(row.get("commercial_short_all", 0))

            net = long - short

            result[symbol] = {
                "commercial_long": long,
                "commercial_short": short,
                "commercial_net": net
            }

            print(f"{symbol} OK → Net: {net}")

        except Exception as e:
            print(f"ERROR parsing {symbol}: {e}")

            result[symbol] = {
                "error": str(e)
            }

    return result


# =========================
# SAVE OUTPUT
# =========================
def save_json(data):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print("\nSaved cot.json successfully")


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    try:
        df = fetch_data()

        cot = build_cot(df)

        save_json(cot)

    except Exception as e:
        print("FATAL ERROR:", e)
        raise
