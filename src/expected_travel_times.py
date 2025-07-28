
############################################################################
### Script to calculate expected times from terminal to all destinations ###
############################################################################

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Load and prepare data ---
df = pd.read_csv("output/london_trains.csv", parse_dates=["arr_time", "dep_time", "origin_time"])

# --- Filter for Tuesday services ---
df = df[df["runs_tue"] == 1].copy()

# --- Adjust for post-midnight arrivals ---
df["arr_time"] = np.where(
    (df["arr_time"].notna()) & (df["origin_time"].notna()) & (df["arr_time"] < df["origin_time"]),
    df["arr_time"] + pd.Timedelta(days=1),
    df["arr_time"]
)

# --- Define time points from 17:00 to 19:00 ---
time_points = [datetime(1900, 1, 1, 17, 0) + timedelta(minutes=i) for i in range(120)]

# --- Define terminal TIPLOCs ---
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

all_results = []

# --- Loop over each terminal ---
for terminal, tiplocs in terminal_tiplocs.items():
    # Get terminal departures based on TIPLOCs
    term_rows = df[df["tiploc_code"].isin(tiplocs) & df["dep_time"].notna()][
        ["train_id", "dep_time", "seq"]
    ].rename(columns={"dep_time": "terminal_dep_time", "seq": "terminal_seq"})
    term_rows["terminal"] = terminal

    # Merge terminal info into full dataset
    merged = df.merge(term_rows, on="train_id")

    # Filter for locations *after* the terminal departure with valid arrival time
    merged = merged[(merged["seq"] > merged["terminal_seq"]) & merged["arr_time"].notna()]

    if merged.empty:
        continue

    for t in time_points:
        eligible = merged[merged["terminal_dep_time"] > t]
        if eligible.empty:
            continue

        eligible = eligible.copy()
        eligible["elapsed_minutes"] = (eligible["arr_time"] - t).dt.total_seconds() / 60
        eligible["minute_block"] = t.strftime("%H:%M")

        # Keep the soonest arrival per stop
        idx = eligible.groupby("stop_name")["arr_time"].idxmin()
        soonest = eligible.loc[idx, [
            "terminal", "stop_name", "elapsed_minutes", "minute_block", "train_id",
            "terminal_dep_time", "arr_time"
        ]]
        all_results.append(soonest)

# --- Combine and save all results ---
results_df = pd.concat(all_results, ignore_index=True)
results_df.to_csv("output/results_df.csv", index=False)

# --- Summarize ---
summary = (
    results_df.groupby(["terminal", "stop_name"])
    .agg(
        expected_minutes=("elapsed_minutes", "mean"),
        samples=("elapsed_minutes", "count")
    )
    .round(1)
    .reset_index()
    .rename(columns={"stop_name": "stop"})
)
summary.to_csv("output/expected_times_to_stops.csv", index=False)

# --- Done ---
print("Done. Outputs saved to:")
print(" - output/results_df.csv")
print(" - output/expected_times_to_stops.csv")
