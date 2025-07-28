
#########################################################################################
### Query the SQLite database for services that start at or stop at a London terminal ###
#########################################################################################

import sqlite3
import pandas as pd
import re
from datetime import datetime

# --- Map each terminal to all its TIPLOCs ---
terminal_tiplocs = {
    'LONDON BLACKFRIARS': ['BLFR'],
    'LONDON CANNON STREET': ['CANONST'],
    'LONDON CHARING CROSS': ['CHRX'],
    'LONDON EUSTON': ['EUSTON'],
    'LONDON FENCHURCH STREET': ['FENCHRS'],
    'LONDON KINGS CROSS': ['KNGX'],
    'LONDON LIVERPOOL STREET': ['LIVST'],
    'LONDON BRIDGE': ['LNDNBDC', 'LNDNBDE', 'LNDNBDG'],
    'LONDON MARYLEBONE': ['MARYLBN'],
    'LONDON PADDINGTON': ['PADTON'],
    'LONDON ST PANCRAS': ['STPADOM', 'STPANCI', 'STPX', 'STPXBOX'], 
    'LONDON VICTORIA': ['VICTRIA', 'VICTRIC', 'VICTRIE'],
    'LONDON WATERLOO': ['WATR', 'WATRLMN', 'WATRLOO', 'WATRLOW']
}

# Flatten all TIPLOCs into a set
all_tiplocs = [code for codes in terminal_tiplocs.values() for code in codes]

# --- Connect to DB ---
conn = sqlite3.connect("db/timetable.db")

placeholders = ",".join(["?"] * len(all_tiplocs))

query = f"""
SELECT
    tl.*,
    t.stp_indicator,
    t.runs_on,
    t.origin,
    t.destination,
    origin_station.station_name AS origin_name,
    dest_station.station_name AS destination_name,
    stop_station.station_name AS stop_name
FROM train_locations tl
JOIN trains t ON t.train_id = tl.train_id
JOIN tiplocs origin_station ON origin_station.tiploc_code = t.origin
JOIN tiplocs dest_station ON dest_station.tiploc_code = t.destination
LEFT JOIN tiplocs stop_station ON stop_station.tiploc_code = tl.tiploc_code
WHERE EXISTS (
    SELECT 1
    FROM train_locations tl2
    WHERE tl2.train_id = tl.train_id AND tl2.tiploc_code IN ({placeholders})
)
"""

df = pd.read_sql_query(query, conn, params=all_tiplocs)
conn.close()

# --- Expand runs_on flags ---
day_names = ["runs_mon", "runs_tue", "runs_wed", "runs_thu", "runs_fri", "runs_sat", "runs_sun"]
for i, name in enumerate(day_names):
    df[name] = df["runs_on"].str[i].fillna("0").astype(int)

# --- Time parsing ---
def clean_time(t):
    if pd.isna(t):
        return None
    t = re.sub(r"[^\d]", "", t)
    if len(t) != 4:
        return None
    return datetime.strptime(t, "%H%M")

df["arr_time"] = df["arrival"].apply(clean_time)
df["dep_time"] = df["departure"].apply(clean_time)

# --- Determine origin time ---
origin_times = df[df["activity"] == "LO"][["train_id", "dep_time"]].rename(columns={"dep_time": "origin_time"})
df = df.merge(origin_times, on="train_id", how="left")

# Fallback to first dep_time if still missing
if df["origin_time"].isna().any():
    fallback = (
        df[df["seq"] == df.groupby("train_id")["seq"].transform("min")][["train_id", "dep_time"]]
        .rename(columns={"dep_time": "origin_time"})
    )
    df = df.drop(columns="origin_time").merge(fallback, on="train_id", how="left")

# --- Elapsed time ---
def compute_elapsed(row):
    current_time = row["arr_time"] if pd.notna(row["arr_time"]) else row["dep_time"]
    origin_time = row["origin_time"]
    if pd.isna(current_time) or pd.isna(origin_time):
        return None
    elapsed = (current_time - origin_time).total_seconds() / 60
    if elapsed < 0:
        elapsed += 1440  # Wrap past midnight
    return elapsed

df["elapsed_from_origin"] = df.apply(compute_elapsed, axis=1)

# --- Output ---
print(df[[
    "train_id", "tiploc_code", "activity", "arrival", "departure",
    "origin_name", "destination_name", "stop_name", "elapsed_from_origin"
] + day_names].head(10))

df.to_csv("output/london_trains.csv", index=False)
print("Saved to output/london_trains.csv")

