import pandas as pd
import requests


def _flatten_dict(d, parent_key="", sep="_"):
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
    elif isinstance(d, list):
        if len(d) > 0:
            items.extend(_flatten_dict(d[0], parent_key, sep=sep).items())
    else:
        items.append((parent_key, d))
    return dict(items)


def get_buy_data(api_key, location="Detroit, MI", n_rows=50):
    url = "https://realtor16.p.rapidapi.com/search/forsale"

    headers = {
        "X-RapidAPI-Key": api_key.strip(),
        "X-RapidAPI-Host": "realtor16.p.rapidapi.com",
    }

    params = {
        "location": location,
        "limit": n_rows,
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        print("Request failed:", response.status_code)
        print(response.text)
        return pd.DataFrame()

    data = response.json()
    listings = data.get("properties", [])

    if not listings:
        print("No data")
        return pd.DataFrame()

    flat_rows = [_flatten_dict(listing) for listing in listings]
    return pd.DataFrame(flat_rows)
