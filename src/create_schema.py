import sqlite3

conn = sqlite3.connect("db/timetable.db")
c = conn.cursor()

# Station reference (TIPLOCs)
c.execute("""
CREATE TABLE IF NOT EXISTS tiplocs (
    tiploc_code TEXT PRIMARY KEY,
    station_name TEXT
);
""")

# Train-level metadata
c.execute("""
CREATE TABLE IF NOT EXISTS trains (
    train_id TEXT PRIMARY KEY,  -- Composite key: uid + stp + start_date
    train_uid TEXT,
    stp_indicator TEXT,
    service_code TEXT,
    runs_on TEXT,
    start_date TEXT,
    end_date TEXT,
    train_status TEXT,
    origin TEXT,
    destination TEXT
);
""")

# Each location visited by a train
c.execute("""
CREATE TABLE IF NOT EXISTS train_locations (
    train_id TEXT,
    seq INTEGER,
    tiploc_code TEXT,
    arrival TEXT,
    departure TEXT,
    platform TEXT,
    activity TEXT,
    PRIMARY KEY (train_id, seq)
);
""")

conn.commit()
conn.close()
print("Schema created.")


