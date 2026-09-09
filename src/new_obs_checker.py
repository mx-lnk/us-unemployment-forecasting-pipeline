import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
import database

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
API_KEY = os.environ['KEY']


# --- returns true if new observations for all series IDs are available on FRED ---

def new_obs_available(series_ids):

    # get latest observation dates of series IDs from FRED
    with requests.Session() as session:

        url = "https://api.stlouisfed.org/fred/series"
        latest_obs_date_fred = {}

        for ID in series_ids:
            params = {"api_key": API_KEY,
                    "file_type": "json",
                    "series_id": ID}

            r = session.get(url=url, params=params, timeout=30)
            r.raise_for_status()

            data = r.json()

            latest_obs = data['seriess'][0]['observation_end']

            latest_obs_date_fred.update({ID: latest_obs})

        latest_obs_date_fred = {
        series_id: datetime.fromisoformat(date)
        for series_id, date in latest_obs_date_fred.items()
        }

    # get latest observation dates of series IDs from db
    latest_obs_date_db = {}
    db = database.get_latest_obs_end(series_ids)
    latest_obs_date_db = {
        series_id: datetime.fromisoformat(date)
        for series_id, date in db
    }

    # compare if for all series IDs are new observations available on FRED
    all_db_obs_dates_outdated = all(
    ID not in latest_obs_date_db
     or latest_obs_date_fred[ID] > latest_obs_date_db[ID]
    for ID in latest_obs_date_db
    )

    return all_db_obs_dates_outdated



if __name__ == "__main__":
    SERIES_IDS = ['UNRATE', 'INDPRO', 'JTSJOL']

    print(new_obs_available(SERIES_IDS))