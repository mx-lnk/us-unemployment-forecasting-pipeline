import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
import database

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
API_KEY = os.environ['KEY']



# --- returns true if all entries of the final selection if series IDs is outdated ---

def check_db_all_entries_outdated(final_series_ids, feature_set):
    # get last update date of series IDs, which are part of the feature set, from FRED
    with requests.Session() as session:

        url = "https://api.stlouisfed.org/fred/series"
        last_update_fred = {}

        for ID in final_series_ids:
            params = {"api_key": API_KEY,
                    "file_type": "json",
                    "series_id": ID}

            r = session.get(url=url, params=params, timeout=30)
            r.raise_for_status()

            data = r.json()

            fred_local_time = datetime.strptime(data['seriess'][0]['last_updated'] + "00", "%Y-%m-%d %H:%M:%S%z")

            last_update_fred.update({ID: fred_local_time.strftime("%Y-%m-%d %H:%M:%S")})

        last_update_fred = {
        series_id: datetime.fromisoformat(date)
        for series_id, date in last_update_fred.items()
        }

    # get last update date of the final IDs from the feature set from the db
    last_update_db = {}
    db = database.get_fred_last_update_local(series_ids=final_series_ids)
    last_update_db = {
        series_id: datetime.fromisoformat(date)
        for series_id, date in db
    }

    all_db_series_outdated = all(
    last_update_fred[ID] > last_update_db[ID]
    for ID in last_update_db
    )

    return all_db_series_outdated

if __name__ == "__main__":
    FINAL_SERIES_IDS = ['UNRATE', 'INDPRO', 'JTSJOL']
    feature_set = ['log10_INDPRO', 'log10_JTSJOL', 'log10_UNRATE', 'UNRATE']

    print(check_db_all_entries_outdated(FINAL_SERIES_IDS, feature_set))