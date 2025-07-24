import os
import requests
import json
from auth import load_credentials, get_token

def download_timetable_zip(token, output_path="data/timetable.zip"):
    url = "https://opendata.nationalrail.co.uk/api/staticfeeds/3.0/timetable"
    headers = {"X-Auth-Token": token}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded timetable ZIP to {output_path}")
    else:
        raise Exception(f"Download failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    creds = load_credentials()
    token = get_token(creds["username"], creds["password"])
    download_timetable_zip(token)
