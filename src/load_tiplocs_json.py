import sqlite3
import json

file_path = "data/timetable/toc-full"  # or actual file path
conn = sqlite3.connect("db/timetable.db")
cur = conn.cursor()

seen = set()

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            record = json.loads(line)
            if "TiplocV1" in record:
                tiploc = record["TiplocV1"]
                code = tiploc["tiploc_code"]
                name = tiploc.get("tps_description") or tiploc.get("description") or "Unknown"

                if code not in seen:
                    cur.execute(
                        "INSERT OR IGNORE INTO tiplocs (tiploc_code, station_name) VALUES (?, ?)",
                        (code, name.strip())
                    )
                    seen.add(code)
        except json.JSONDecodeError:
            continue

conn.commit()
conn.close()
print(f"TIPLOCs loaded: {len(seen)}")




