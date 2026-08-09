import sqlite3
from pathlib import Path
from functools import wraps

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "us_unemployment.db"
SQL_DIR = ROOT_DIR / "sql"

def db_connection_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        con = sqlite3.connect(DB_PATH)
        con.execute("PRAGMA foreign_keys = ON;")

        try:
            result = func(con, *args, **kwargs)
            con.commit()
            return result
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    return wrapper



@db_connection_handler
def create_tables(con):
    with open(SQL_DIR / "create_tables.sql", encoding="utf-8") as f:
        con.executescript(f.read())

@db_connection_handler
def upsert_fred_series(con, fred_series_data):
    with open(SQL_DIR / "upsert_FREDSeries.sql", encoding="utf-8") as f:
        sql = f.read()
    con.execute(sql, fred_series_data) 

"""
1. Create tables
2. Populate FREDSeries from https://api.stlouisfed.org/fred/series? endpoint
3. Write fetched observations to 'FREDObservations'
4. Write computed features to 'MonthlyFeatures'
"""

if __name__ == "__main__":
    create_tables()
    upsert_fred_series()