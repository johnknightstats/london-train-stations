# geocode_terminals.py

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os

# List of terminal names
terminals = [
    'LONDON BLACKFRIARS',
    'LONDON CANNON STREET',
    'LONDON CHARING CROSS',
    'LONDON EUSTON',
    'LONDON FENCHURCH STREET',
    'LONDON KINGS CROSS',
    'LONDON LIVERPOOL STREET',
    'LONDON BRIDGE',
    'LONDON MARYLEBONE',
    'LONDON PADDINGTON',
    'LONDON ST PANCRAS',
    'LONDON VICTORIA',
    'LONDON WATERLOO'
]

df = pd.DataFrame({'terminal': terminals})

# Set up geocoder
geolocator = Nominatim(user_agent="terminal_mapper")
geocode = RateLimiter(lambda query: geolocator.geocode(query + ", London, UK"), 
                      min_delay_seconds=1, max_retries=3, error_wait_seconds=5)

# Geocode function
def get_lat_lon(terminal):
    try:
        location = geocode(terminal)
        if location:
            return pd.Series([location.latitude, location.longitude])
    except Exception as e:
        print(f"Failed to geocode {terminal}: {e}")
    return pd.Series([None, None])

# Apply geocoding
df[['lat', 'lon']] = df['terminal'].apply(get_lat_lon)

# Drop failures
df = df.dropna(subset=['lat', 'lon'])

# Save output
os.makedirs("output", exist_ok=True)
df.to_csv("output/london_terminals_geocoded.csv", index=False)
print("Saved geocoded terminals to output/london_terminals_geocoded.csv")
