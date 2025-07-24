import json

# Path to your JSON file
file_path = "data/timetable/toc-full"

# Number of records to inspect
num_records = 10

def inspect_keys(d, prefix=""):
    if isinstance(d, dict):
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            print(full_key)
            inspect_keys(v, prefix=full_key)
    elif isinstance(d, list) and d and isinstance(d[0], dict):
        print(f"{prefix}[]")
        inspect_keys(d[0], prefix=prefix + "[]")

# Counter
seen = 0

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if '"JsonScheduleV1"' not in line:
            continue

        record = json.loads(line)
        sched = record.get("JsonScheduleV1", {})

        # Only show 'Create' transaction_type schedules
        if sched.get("transaction_type") != "Create":
            continue

        print(f"\n--- Record {seen+1} ---")
        inspect_keys(sched)

        seen += 1
        if seen >= num_records:
            break


