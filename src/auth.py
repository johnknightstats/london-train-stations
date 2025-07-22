import requests
import json
import os

def load_credentials():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def get_token(username, password):
    url = 'https://opendata.nationalrail.co.uk/authenticate'
    payload = {'username': username, 'password': password}
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        token = response.text.strip()
        print("Token retrieved successfully.")
        return token
    else:
        raise Exception(f"Authentication failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    creds = load_credentials()
    token = get_token(creds['username'], creds['password'])
    print("Your token:", token)
