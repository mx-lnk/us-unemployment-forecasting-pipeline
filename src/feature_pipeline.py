import numpy as np
import pandas as pd
import database

def get_features():
    # Fetch all observations from the db
    data = database.db_requester_fetchall(sql_script="all_obs_FREDObservations.sql")

    # Import raw data into df_raw
    df_raw = pd.DataFrame(data, columns=['series_id', 'year_month', 'value', 'timestamp'])
    df_raw['year_month'] = pd.to_datetime(df_raw['year_month'])

    # Pivot df_raw, so that each feature has its own column 
    df = df_raw.pivot(
        index='year_month',
        columns='series_id',
        values='value'
    ).reset_index()
    df['year_month'] = df['year_month'].dt.to_period('M')
    df.columns.name = None

    # In a previous version the df was imputed with linear interpolation.
    # I scrapped this due to potential look-ahead leakage when backtesting.
    df_clean = df.copy()

    # construct a master df containing all features
    df_features = pd.DataFrame({
        "year_month_t": df_clean['year_month'].copy(),
        "log_10_UNRATE_t": df_clean['UNRATE'].apply(np.log10).copy(),
        "log_10_INDPRO_t-1": df_clean['INDPRO'].shift(1).apply(np.log10).copy(),
        "log_10_JTSJOL_t-1": df_clean['JTSJOL'].shift(1).apply(np.log10).copy(),
        "UNRATE_t": df_clean['UNRATE'].copy(),
        "INDPRO_t-1": df_clean['INDPRO'].shift(1).copy(),
        "JTSJOL_t-1": df_clean['JTSJOL'].shift(1).copy(),
        "UNRATE_t+1": df_clean['UNRATE'].shift(-1).copy(),
    })

    # get the indexes of row with NaN values, excluding the target column UNRATE_t+1 which naturally has a NaN in its last row.
    nan_rows = df_features[df_features.iloc[:,1:-1].isna().any(axis=1)].index.to_list()
    df_features = df_features.drop(nan_rows, axis=0).reset_index(drop=True)
    df_features = df_features.sort_values("year_month_t", ascending=True).reset_index(drop=True)

    # safeguards against duplicate values and non-ascending "year_month_t" column
    if df_features["year_month_t"].duplicated().any():
        raise ValueError("Duplicate periods detected.")
    if not df_features["year_month_t"].is_monotonic_increasing:
        raise ValueError("Periods are not chronologically ordered.")

    return df_features

if __name__ == "__main__":
    get_features()

