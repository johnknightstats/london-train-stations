
##########################################################################
### Script to create map of London railway stations with commute times ###
##########################################################################

import pandas as pd
import folium
import os
from branca.colormap import linear

# Load geocoded stop data
df = pd.read_csv("output/expected_time_to_stops_geocoded.csv")

# Filter out rows where terminal == stop
df = df[df['terminal'] != df['stop']]

# Filter out long travel times
df = df[df['expected_minutes'] <= 120]

# Set up map centered on London
m = folium.Map(location=[51.5074, -0.1278], zoom_start=10, tiles="CartoDB positron")

# Color scale: green (short) to red (long)
min_minutes = df['expected_minutes'].min()
max_minutes = df['expected_minutes'].max()
colormap = linear.RdYlGn_11.scale(min_minutes, max_minutes).to_step(n=12)
colormap.colors = list(colormap.colors)[::-1]  # Reverse to make green = short
colormap.caption = 'Expected Minutes from Terminal'
colormap.add_to(m)

# Load terminal names to exclude them from colored dot layer
try:
    terminal_names = pd.read_csv("output/london_terminals_geocoded.csv")['terminal'].str.upper().tolist()
except FileNotFoundError:
    terminal_names = []
    print("Warning: london_terminals_geocoded.csv not found. Skipping terminal exclusion.")

# Group by stop: one dot per stop
grouped = (
    df.groupby('stop')
      .agg({
          'lat': 'first',
          'lon': 'first',
          'terminal': lambda x: list(x),
          'expected_minutes': lambda x: list(x)
      })
      .reset_index()
)

# Remove terminals from stops layer
grouped = grouped[~grouped['stop'].str.upper().isin(terminal_names)]

# --- Create one FeatureGroup per terminal ---
terminal_layers = {}
for term in sorted(df['terminal'].unique()):
    terminal_layers[term] = folium.FeatureGroup(name=term)

# Add markers for stops (shared across layers)
for _, row in grouped.iterrows():
    lat, lon = row['lat'], row['lon']
    min_time = min(row['expected_minutes'])
    color = colormap(min_time)

    # Tooltip text, sorted by expected_minutes
    lines = [f"<b>{row['stop']}</b>"]
    pairs = sorted(zip(row['terminal'], row['expected_minutes']), key=lambda x: x[1])
    for term, mins in pairs:
        lines.append(f"- {term}: {mins:.1f} min")
    tooltip = "<br>".join(lines)

    for term in row['terminal']:
        if term in terminal_layers:
            marker = folium.CircleMarker(
                location=(lat, lon),
                radius=6,
                popup=folium.Popup(tooltip, max_width=300),
                tooltip=tooltip,
                color=color,
                fill=True,
                fill_opacity=0.8,
                fill_color=color
            )
            terminal_layers[term].add_child(marker)


# Add all terminal layers to the map
for group in terminal_layers.values():
    group.add_to(m)

# Add checkbox controls
folium.LayerControl(collapsed=False).add_to(m)

# --- Add black star markers for London terminals ---
try:
    terminals = pd.read_csv("output/london_terminals_geocoded.csv")

    for _, row in terminals.iterrows():
        folium.map.Marker(
            location=(row['lat'], row['lon']),
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 18pt; color: black; text-align: center;">★</div>"""
            ),
            popup=folium.Popup(f"<b>{row['terminal']}</b>", max_width=200),
            tooltip=row['terminal']
        ).add_to(m)

except FileNotFoundError:
    print("Warning: london_terminals_geocoded.csv not found. Skipping terminal markers.")

# Save the map
os.makedirs("output", exist_ok=True)
m.save("output/london_commuter_stations.html")
print("Map saved to output/london_commuter_stations.html")



