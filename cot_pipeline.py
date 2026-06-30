import requests
import pandas as pd
import json

OUTPUT_FILE = "cot.json"

URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# =========================
# REALISTIC CFTC KEYWORDS (broader matching)
# =========================
SYMBOL_MAP = {
    "ES": ["S&P 500", "E-MINI S&P", "E-MINI S&P 500", "SP500"],
    "CL": ["CRUDE OIL", "LIGHT SWEET CRUDE", "WTI"],
    "DX": ["DOLLAR INDEX", "USD INDEX", "U.S. DOLLAR INDEX"]
}


# =========================
# FETCH
# =========================
def fetch_data():
    print("Fetching CFTC data...")

    r = requests.get(URL, timeout=30)

    if r.status_code != 200:
        raise Exception(f"CFTC API error: {r.status_code}")

    data = r.json()

    if not data:
        raise Exception("Empty CFTC response")

    df = pd.DataFrame(data)

    print("Rows:", len(df))
    print("Columns:", df.columns.tolist())

    return df


# =========================
# MATCH ENGINE (FIXED)
# =========================
def find_latest_match(df, keywords):

    if df.empty:
        return None

    # safe column detection
    name_col = None

    for c in df.columns:
        if "contract" in c.lower() and "name" in c.lower():
            name_col = c
            break

    if name_col is None:
        print("Available columns:", df.columns.tolist())
        raise Exception("No contract name column found")

    mask = pd.Series([False] * len(df))

    for kw in keywords:
        mask = mask | df[name_col].str.contains(kw, case=False, na=False)

    filtered = df[mask]

    print(f"Matches: {len(filtered)} for {keywords}")

    if filtered.empty:
        return None

    # find date column safely
    date_col = None

    for c in df.columns:
        if "date" in c.lower():
            date_col = c
            break

    if date_col:
        filtered = filtered.sort_values(date_col)

    return filtered.iloc[-1]


# =========================
# BUILD COT
# =========================
def build_cot(df):

    result = {}

    for symbol, keywords in SYMBOL_MAP.items():

        print(f"\nProcessing {symbol}...")

        row = find_latest_match(df, keywords)

        if row is None:
            print(f"NO MATCH: {symbol}")

            result[symbol] = {
                "error": "no match found"
            }
            continue

        try:
            # dynamic column fallback (CFTC changes often)
            long = 0
            short = 0

            for c in df.columns:
                if "long" in c.lower() and "comm" in c.lower():
                    long = float(row.get(c, 0) or 0)

                if "short" in c.lower() and "comm" in c.lower():
                    short = float(row.get(c, 0) or 0)

            net = long - short

            result[symbol] = {
                "commercial_long": long,
                "commercial_short": short,
                "commercial_net": net
            }

            print(f"{symbol} → NET {net}")

        except Exception as e:
            print(f"ERROR {symbol}: {e}")

            result[symbol] = {
                "error": str(e)
            }

    return result


# =========================
# SAVE
# =========================
def save_json(data):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print("\nSaved cot.json")


# =========================
# RUN
# =========================
if __name__ == "__main__":

    try:
        df = fetch_data()

        cot = build_cot(df)

        save_json(cot)

        print("\nSUCCESS")

    except Exception as e:
        print("\nFATAL ERROR:", e)
        raise
