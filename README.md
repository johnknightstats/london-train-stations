# london-train-stations

This project analyzes travel times from all 13 London railway terminals to the destinations they serve across Greater London and surrounding areas. The goal is to understand how accessible different parts of the region are by rail, using real-world timetable data.

🗺️ **Explore the results**:
- 📘 [Read the full article](https://johnknightstats.com/posts/london_rail_stations/)
- 🛠️ [View the full interactive map](https://johnknightstats.com/tools/london-commuter-map.html)

---

## ✨ What This Project Does

- Downloads official Network Rail timetable files
- Loads the data into a structured SQLite database
- Calculates **expected journey time** from each London terminal to all reachable stations
- Geocodes station locations
- Generates an interactive map with commute time tooltips

---

## 🗂 Folder Structure

```
├── config/ # Stores a credentials template (do not share secrets!)
├── data/ # Raw downloaded National Rail data (ignored)
├── db/ # SQLite database storing structured schedule data
├── output/ # Final travel time results and map outputs
├── src/ # Main Python scripts
│ ├── expected_travel_times.py # Calculates expected journey durations
│ ├── create_map.py # Builds HTML map with stations and travel times
│ ├── download_timetable.py # Downloads raw timetable files
│ ├── geocode_stations.py # Gets lat/lon for destinations
│ ├── geocode_terminals.py # Gets lat/lon for London terminals
│ ├── load_schedules_json.py # Loads JSON schedules into SQLite
│ ├── get_london_terminal_services.py # Filters database for London-serving trains
│ └── ...
├── requirements.txt # Python dependencies
├── .gitignore
└── README.md
```

---

## 🛠 Requirements

Install dependencies with:

pip install -r requirements.txt

You’ll also need:

    A National Rail Data Portal account to download timetable data

    A .json config file with your credentials (see config_template.json)
    
## 🔐 Credentials

Create a config/config.json file with the following format:

{
  "username": "your_username",
  "password": "your_password"
}

This file is ignored by git to keep your login secure.

## 📍 Output

If the scripts run successfully, you’ll get:

    A CSV of expected travel times to all reachable stations

    A geocoded dataset of stations and terminals

    An HTML map showing commute accessibility

## 🚫 Notes

    This project does not include raw data or databases — they are large and not publicly shareable.

    If you’d like to recreate the analysis, follow the steps in src/download_timetable.py and src/create_schema.py.

## 📄 License

MIT License — see LICENSE file for details.

## ✍️ Author

John Knight
https://johnknightstats.com