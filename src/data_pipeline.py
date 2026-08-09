import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
import database

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
API_KEY = os.environ['KEY']
SERIES_IDS = ['UNRATE', 'PAYEMS', 'ICSA', 'INDPRO', 'JTSJOL']

def fred_series_data_pipeline():
    # Fetch data from FRED for FREDSeries table
    url="https://api.stlouisfed.org/fred/series"

    fred_series_params = {
    "api_key": API_KEY,
    "file_type": "json"
    }

    with requests.Session() as session:
        for series_id in SERIES_IDS:
            params = {
                **fred_series_params,
                "series_id": series_id
            }

            r = session.get(url=url, params=params, timeout=30)
            r.raise_for_status()

            data = r.json()

            fred_local_time = datetime.strptime(data['seriess'][0]['last_updated'] + "00", "%Y-%m-%d %H:%M:%S%z")
            fred_utc_time = fred_local_time.astimezone(timezone.utc)

            fred_series_data = {
                "series_id": data['seriess'][0]['id'],
                "title": data['seriess'][0]['title'],
                "frequency": data['seriess'][0]['frequency'],
                "units": data['seriess'][0]['units'],
                "observation_start": data['seriess'][0]['observation_start'],
                "last_update_local_time": fred_local_time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_update_utc":fred_utc_time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Upsert the fetched data to the db ID by ID
            database.upsert_fred_series(fred_series_data=fred_series_data)


if __name__ == "__main__":
    fred_series_data_pipeline()
