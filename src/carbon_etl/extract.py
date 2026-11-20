"""Extract: fetch one day of regional carbon intensity data from the UK Carbon Intensity API."""
import time
from datetime import date

import requests

BASE_URL = "https://api.carbonintensity.org.uk/regional/intensity/{day}/pt24h"


def fetch_day(target_date: date, retries: int = 3, timeout: int = 20) -> list:
    """Return the API's 'data' list for the 24 hours before target_date.

    Retries on network errors, rate limits (429) and server errors (5xx).
    Fails immediately on other errors, such as a bad URL (404).
    """
    url = BASE_URL.format(day=target_date.isoformat())
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers={"Accept": "application/json"}, timeout=timeout)
        except requests.RequestException as err:
            print(f"Attempt {attempt}: request failed ({err})")
            time.sleep(5 * attempt)
            continue

        if response.status_code == 200:
            data = response.json()["data"]
            print(f"Fetched {len(data)} half-hour intervals for {target_date}")
            return data
        if response.status_code == 429 or response.status_code >= 500:
            print(f"Attempt {attempt}: status {response.status_code}, retrying...")
            time.sleep(5 * attempt)
            continue
        response.raise_for_status()

    raise RuntimeError(f"Could not fetch data for {target_date} after {retries} attempts")