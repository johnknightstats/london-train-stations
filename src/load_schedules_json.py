import sqlite3
import json

conn = sqlite3.connect("db/timetable.db")
c = conn.cursor()

train_count = 0
location_count = 0

with open("data/timetable/toc-full", "r", encoding="utf-8") as f:
    for line in f:
        if '"JsonScheduleV1"' not in line:
            continue

        try:
            record = json.loads(line)
            sched = record["JsonScheduleV1"]

            # Only process newly created schedules
            if sched.get("transaction_type") != "Create":
                continue

            # Extract core metadata
            train_uid = sched.get("CIF_train_uid")
            stp_indicator = sched.get("CIF_stp_indicator")
            runs_on = sched.get("schedule_days_runs")
            start_date = sched.get("schedule_start_date")
            end_date = sched.get("schedule_end_date")
            service_code = sched.get("train_service_code")
            locations = sched.get("schedule_segment", {}).get("schedule_location", [])

            if not train_uid or not stp_indicator or not start_date or not locations:
                continue

            origin = locations[0].get("tiploc_code")
            destination = locations[-1].get("tiploc_code")

            if not origin or not destination:
                continue

            # Use composite key
            train_id = f"{train_uid}_{stp_indicator}_{start_date}"

            c.execute("""
                INSERT OR IGNORE INTO trains (
                    train_id, train_uid, stp_indicator, service_code,
                    runs_on, start_date, end_date, origin, destination
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                train_id,
                train_uid,
                stp_indicator,
                service_code,
                runs_on,
                start_date,
                end_date,
                origin,
                destination
            ))
            train_count += 1

            for i, loc in enumerate(locations):
                tiploc = loc.get("tiploc_code")
                public_arrival = loc.get("public_arrival")
                public_departure = loc.get("public_departure")

                if not tiploc or (not public_arrival and not public_departure):
                    continue

                c.execute("""
                    INSERT OR IGNORE INTO train_locations (
                        train_id, seq, tiploc_code, arrival, departure, platform, activity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    train_id,
                    i,
                    tiploc.strip(),
                    public_arrival,
                    public_departure,
                    loc.get("platform"),
                    loc.get("location_type")
                ))
                location_count += 1

        except json.JSONDecodeError:
            continue  # Skip badly formatted lines

conn.commit()
conn.close()

print(f"Trains loaded: {train_count}")
print(f"Locations loaded: {location_count}")
