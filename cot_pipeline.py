import requests
import pandas as pd
import json

OUTPUT_FILE = "cot.json"

URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# =========================
# SYMBOL MAPPING (robust keyword matching)
# =========================
SYMBOL_MAP = {
    "ES": ["S&P", "E-MINI", "SP 500", "E-MINI S&P"],
    "CL": ["CRUDE OIL", "LIGHT SWEET", "NYMEX"],
    "DX": ["DOLLAR INDEX", "U.S. DOLLAR", "ICE DOLLAR"]
}


# =========================
# FETCH DATA SAFELY
# =========================
def fetch_data():
    print("Fetching CFTC data...")

    r = requests.get(URL, timeout=30)

    if r.status_code != 200:
        raise Exception(f"CFTC API error: {r.status_code}")

    data = r.json()

    if not data:
        raise Exception("CFTC returned empty dataset")

    df = pd.DataFrame(data)

    print("Rows received:", len(df))
    print("Columns:", list(df.columns))

    return df


# =========================
# FIND MATCH SAFE
# =========================
def find_latest_match(df, keywords):

    if df.empty:
        return None

    if "contract_market_name" not in df.columns:
        raise Exception(f"Missing column contract_market_name. Columns: {df.columns}")

    mask = pd.Series([False] * len(df))

    for kw in keywords:
        mask = mask | df["contract_market_name"].str.contains(kw, case=False, na=False)

    filtered = df[mask]

    print(f"Matches found: {len(filtered)} for {keywords}")

    if filtered.empty:
        return None

    # sort by date if available
    if "report_date_as_yyyy_mm_dd" in filtered.columns:
        filtered = filtered.sort_values("report_date_as_yyyy_mm_dd")

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
            print(f"WARNING: No match for {symbol}")

            result[symbol] = {
                "error": "no data found"
            }
            continue

        try:
            long = float(row.get("commercial_long_all", 0) or 0)
            short = float(row.get("commercial_short_all", 0) or 0)

            net = long - short

            result[symbol] = {
                "commercial_long": long,
                "commercial_short": short,
                "commercial_net": net
            }

            print(f"{symbol} OK → Net: {net}")

        except Exception as e:
            print(f"ERROR processing {symbol}: {str(e)}")

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

    print("\nSaved cot.json")


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    try:
        df = fetch_data()

        cot = build_cot(df)

        save_json(cot)

        print("\nSUCCESS: Pipeline completed")

    except Exception as e:
        print("\nFATAL ERROR:")
        print(str(e))
        raise
