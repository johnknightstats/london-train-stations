# geocode_stations.py

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os

# Load original data
df = pd.read_csv("output/expected_times_to_stops.csv")

# Ensure output folder exists
os.makedirs("output", exist_ok=True)

# Load or create geocode cache
cache_file = "output/station_geocode_cache.csv"
try:
    cache = pd.read_csv(cache_file)
    print(f"Loaded geocode cache with {len(cache)} entries.")
except FileNotFoundError:
    cache = pd.DataFrame(columns=["stop", "lat", "lon"])
    print("No cache found. Starting fresh.")

# Identify new stops not yet in cache
new_stops = df[['stop']].drop_duplicates().merge(
    cache[['stop']], on='stop', how='left', indicator=True
)
new_stops = new_stops[new_stops['_merge'] == 'left_only'].drop(columns=['_merge'])

# Set up geolocator with retry and timeout
# Set up geolocator and rate limiter (pass timeout inside lambda)
geolocator = Nominatim(user_agent="train_station_mapper")

geocode = RateLimiter(
    lambda query: geolocator.geocode(query, timeout=10),
    min_delay_seconds=1,
    max_retries=3,
    error_wait_seconds=5
)

# Manual overrides: stop → (lat, lon)
manual_geocodes = {
    "STRATFORD": (51.541216910923026, -0.0034744189350195444),
    "STONELEIGH": (51.36340389724217, -0.24825343247471507),
    "SUTTON (SURREY)": (51.35947718915612, -0.19083746203872157),
    "KINGSTON": (51.41275238789358, -0.3010247874487608),
    "WEST WICKHAM": (51.38132988530406, -0.013866260466931847),
    "BERWICK": (50.8404716120835, 0.16631442611891684),
    "NORTHUMBERLAND PARK": (51.60283163545101, -0.05450684907762573),
    "BELLINGHAM": (51.43350972790578, -0.019065250415451637),
    "BELMONT": (51.34393340937643, -0.19796313163288828),
    "STONEGATE": (51.020015358591195, 0.3639084524944862),
    "HORSLEY": (51.279516406797505, -0.43529438375097584),
    "TWYFORD": (51.47538519949915, -0.8629200206022135),
    "LONDON WATERLOO (EAST)": (51.50445361421251, -0.10987598559122345),
    "LEE": (51.449512838136314, 0.013787854881084178)
}

# Function to geocode a stop
def get_lat_lon(row):
    stop = row['stop'].upper()
    country = row['country']

    # Use manual override if available
    if stop in manual_geocodes:
        lat, lon = manual_geocodes[stop]
        print(f"Using manual geocode for {stop}: {lat}, {lon}")
        return pd.Series([stop, lat, lon])

    # Otherwise use Nominatim
    try:
        location = geocode(f"{stop}, {country}, UK")
        if location:
            return pd.Series([stop, location.latitude, location.longitude])
    except Exception as e:
        print(f"Failed to geocode {stop}: {e}")
    return pd.Series([stop, None, None])


# Geocode only new stops
if not new_stops.empty:
    print(f"Geocoding {len(new_stops)} new stops...")
    # Merge country info for new stops
    df['country'] = 'England'
    new_stops = new_stops.merge(df[['stop', 'country']].drop_duplicates(), on='stop', how='left')

    # Apply geocoding function row-wise
    geocoded_new = new_stops.apply(get_lat_lon, axis=1)
    geocoded_new.columns = ['stop', 'lat', 'lon']

    # Append to cache and save
    cache = pd.concat([cache, geocoded_new], ignore_index=True)
    cache.to_csv(cache_file, index=False)
else:
    print("No new stops to geocode.")

# Merge cached coordinates with original data
df = df.merge(cache, on="stop", how="left")

# Drop rows where geocoding failed
geocoded_df = df.dropna(subset=["lat", "lon"])
print(f"Successfully geocoded {len(geocoded_df)} of {len(df)} rows.")

# Save geocoded output
geocoded_df.to_csv("output/expected_time_to_stops_geocoded.csv", index=False)
print("Saved geocoded data to output/expected_time_to_stops_geocoded.csv")

