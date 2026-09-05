import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import database
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
API_KEY = os.environ['KEY']

def fred_series_data_pipeline(series_ids):
    # Fetch data from FRED for FREDSeries table
    url = "https://api.stlouisfed.org/fred/series?"
    results = []

    with requests.Session() as session:
        for ID in series_ids:
            params = {
                "api_key": API_KEY,
                "file_type": "json",
                "series_id": ID
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
    database.db_upsert_insert_many(sql_script="upsert_FREDSeries.sql", data=results)



def fred_observations_data_pipeline(series_ids):
    # Get earliest common observations start date (ecos) and deduct one month to get data for the t-1 lagged features
    ecos = datetime.strptime(database.earliest_common_obs_start(), "%Y-%m-%d")
    obs_start = datetime.strftime((ecos - relativedelta(months=1)), "%Y-%m-%d")

    # Fetch raw observations from FRED for FREDObservations table
    url = 'https://api.stlouisfed.org/fred/series/observations'
    results = []

    with requests.Session() as session:
        for ID in series_ids:
            params = {
                "api_key": API_KEY,
                "file_type": "json",
                "sort_order": "asc",
                "units": "lin",
                "observation_start": obs_start,
                "series_id": ID
            }

            r = session.get(url=url, params=params, timeout=30)
            r.raise_for_status()

            data = r.json()
            entries = data['observations']

            for entry in entries:
                fred_observations_data = {
                    "series_id": ID,
                    "observation_date": entry['date'],
                    "native_value": entry['value']
                }
            
                results.append(fred_observations_data)

    # Write all entires as upsert to the db
    database.db_upsert_insert_many(sql_script="upsert_FREDObservations.sql", data=results)

    # Replace all missing values in FREDObservations NativeValue to NULL for consistency
    database.set_missing_observations_null()



if __name__ == "__main__":
    SERIES_IDS = ['UNRATE', 'INDPRO', 'JTSJOL']

    # fred_series_data_pipeline(series_ids=SERIES_IDS)
    # fred_observations_data_pipeline(series_ids=SERIES_IDS)