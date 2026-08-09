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
    url = "https://api.stlouisfed.org/fred/series?"
    results = []

    with requests.Session() as session:
        for series_id in SERIES_IDS:
            params = {
                "api_key": API_KEY,
                "file_type": "json",
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

            results.append(fred_series_data)

    # Write all entires as upsert to the db
    database.db_upsert_many(sql_script="upsert_FREDSeries.sql", data=results)



def fred_observations_data_pipeline():
    # Get earliest common observations start date, short ecos
    ecos = database.earliest_common_obs_start()

    # Fetch raw observations from FRED for FREDObservations table
    url = 'https://api.stlouisfed.org/fred/series/observations'
    results = []

    with requests.Session() as session:
        for series_id in SERIES_IDS:
            params = {
                "api_key": API_KEY,
                "file_type": "json",
                "sort_order": "asc",
                "units": "lin",
                "observation_start": ecos,
                "series_id": series_id
            }

            r = session.get(url=url, params=params, timeout=30)
            r.raise_for_status()

            data = r.json()
            entries = data['observations']

            for entry in entries:
                fred_observations_data = {
                    "series_id": series_id,
                    "observation_date": entry['date'],
                    "native_value": entry['value']
                }
            
                results.append(fred_observations_data)

    # Write all entires as upsert to the db
    database.db_upsert_many(sql_script="upsert_FREDObservations.sql", data=results)






if __name__ == "__main__":
    fred_series_data_pipeline()
    fred_observations_data_pipeline()
