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
def earliest_common_obs_start(con):
    with open(SQL_DIR / "most_recent_obs_start.sql", encoding="utf-8") as f:
        cursor = con.execute(f.read())
    earliest_common_observation_start = cursor.fetchone()[0]   
    return earliest_common_observation_start

@db_connection_handler
def db_upsert_insert_many(con, sql_script, data):
    with open(SQL_DIR / sql_script, encoding="utf-8") as f:
        sql = f.read()
    con.executemany(sql, data)

@db_connection_handler
def set_missing_observations_null(con):
    with open(SQL_DIR / "set_missing_FREDObservations_NULL.sql", encoding="utf-8") as f:
        con.executescript(f.read())

@db_connection_handler
def db_requester_fetchall(con, sql_script):
    with open(SQL_DIR / sql_script, encoding="utf-8") as f:
        cursor = con.execute(f.read())
    data = cursor.fetchall()
    return data

@db_connection_handler
def get_latest_obs_end(con, series_ids):
    
    with open(SQL_DIR / "get_latest_obs_end.sql", encoding="utf-8") as f:
        query = f.read()

    placeholders = ", ".join("?" for ID in series_ids)
    query = query.format(placeholder_ids=placeholders)
    cursor = con.execute(query, series_ids)
    return cursor.fetchall()

if __name__ == "__main__":
    create_tables()
    # earliest_common_obs_start()
    # set_missing_observations_null()
