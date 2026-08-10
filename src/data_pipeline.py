import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
import database
import numpy as np
import pandas as pd

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

    # Replace all missing values in FREDObservations NativeValue to NULL for consistency
    database.set_missing_observations_null()



def monthly_features_data_pipeline():
    # Retrieve the NativeValues from FREDObservations
    native_observations = database.db_requester_fetchall("all_obs_FREDObservations.sql")

    # Convert all dates to datetime with format YYYY-MM and drop the timestamp column
    arr = np.array(native_observations)
    arr = np.delete(arr,[False, False, False, True], 1)
    arr[:][:,1] = arr[:][:,1].astype("datetime64[M]")

    # Get the ICSA rows
    idx_icsa = np.where(arr=='ICSA')[0]

    # Split the data into an ICSA and none-ICSA array
    icsa_arr = arr[idx_icsa]
    none_icsa_arr = np.delete(arr, idx_icsa, 0)

    # Aggregate monthly ICSA with a Pandas df
    column_names = ['series_id', 'month_year', 'monthly_value']
    df_icsa = pd.DataFrame(icsa_arr, columns=column_names)
    df_monthly_icsa = (
        df_icsa.groupby("month_year", as_index=False).agg({
            "series_id": "last",
            "monthly_value": lambda x: None if x.isna().any() else x.sum()
        })
    )
    df_monthly_icsa.insert(
        0,
        df_monthly_icsa.columns[1],
        df_monthly_icsa.pop(df_monthly_icsa.columns[1])
    )

    # Put the none-ICSA data into a separate df
    df_none_ics = pd.DataFrame(none_icsa_arr, columns=column_names)

    # Concatenate both dfs and export the as a dict, writable for the db
    df_all_monthly = pd.concat([df_none_ics, df_monthly_icsa], ignore_index=True)
    df_all_monthly = df_all_monthly.astype(object).where(
        pd.notna(df_all_monthly),
        None
    )
    db_ready_monthly_values = df_all_monthly.to_dict(orient='records')

    # Upsert the dict into the MonthlyFeatures table
    database.db_upsert_many(sql_script="upsert_MonthlyFeatures.sql", data=db_ready_monthly_values)


if __name__ == "__main__":
    fred_series_data_pipeline()
    fred_observations_data_pipeline()
    monthly_features_data_pipeline()