import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from pathlib import Path
from dotenv import load_dotenv
import database

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

API_KEY = os.environ['KEY']

def updater():

    # --- Fetching and updating the ActualUNRATEHistorical in Runs table ---

    url = "https://api.stlouisfed.org/fred/series/observations"
    null_dates = database.db_requester_fetchall(sql_script="get_null_dates.sql")
    hist_unrates = []

    with requests.Session() as session:
    
        for date in null_dates:

            params = {
                "api_key": API_KEY,
                "observation_start": datetime.strptime(date[0], "%Y-%m").strftime("%Y-%m-%d"),
                "observation_end": datetime.strptime(date[0], "%Y-%m").strftime("%Y-%m-%d"),
                "realtime_start": "1776-07-04",
                "realtime_end": "9999-12-31",
                "output_type": "4",
                "file_type": "json",
                "series_id": "UNRATE"
            }

            r = session.get(url=url, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            
            forecast_target_t1 = date[0]
            if len(data['observations']) != 0:
                def unrate_availability(unrate):
                    try:
                        return float(unrate)
                    except(ValueError, TypeError):
                        return None
                release_date_historical = data['observations'][0]['realtime_start']
                actual_unrate_historical = unrate_availability(data['observations'][0]['value'])
            else: release_date_historical, actual_unrate_historical = None, None

            hist_unrates.append({"forecast_target_t1": forecast_target_t1,
                                    "release_date_historical": release_date_historical,
                                    "actual_unrate_historical": actual_unrate_historical})
            
    database.db_upsert_insert_many(sql_script="update_unrate_historical.sql", data=hist_unrates)

    # --- Update Runs table with ActualUNRATELive from FREDObservations table ---
    database.execute_script(sql_script="update_unrate_live.sql")

    # --- Calculate and update ModelAbsError / Naive AbsError via SQLite for both live and historical UNRATE ---
    database.execute_script(sql_script="update_abs_error.sql")
    
    # --- Update the Forecasts table with data from the now completed Runs table by matching the RowID ---
    database.execute_script(sql_script="update_forecasts.sql")


if __name__ == "__main__":
    updater()