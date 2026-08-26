import numpy as np
import pandas as pd
from pathlib import Path
import database

def get_all_features():
    # Fetch all complete months from the db
    data = database.db_requester_fetchall(sql_script="all_MonthlyFeatures.sql")

    # Import raw data into df_raw
    df_raw = pd.DataFrame(data, columns=['series_id', 'month_year', 'value', 'timestamp'])
    df_raw['month_year'] = pd.to_datetime(df_raw['month_year'])

    # Reformat df_raw into a suitable format
    df = df_raw.pivot(
        index='month_year',
        columns='series_id',
        values='value'
    ).reset_index()
    df['month_year'] = df['month_year'].dt.to_period('M')
    df.columns.name = None

    # Impute missing values with linear interpolation
    features = ['ICSA', 'INDPRO', 'JTSJOL', 'PAYEMS', 'UNRATE']
    df_imputed = df.copy()
    df_imputed[features] = df[features].interpolate(method="linear")
    df_imputed[df_imputed.isna().any(axis=1)]

    # construct a master df containing all features
    time_frames = [1, 3, 6, 12]
    df_features = df_imputed.copy()

    for feature in features:
        df_features[f"log10_{feature}"] = df_features[feature].apply(np.log10)

    for feature in features[0:4]:
        df_features[f"{feature}_pct_change"] = df_features[feature].pct_change()

    df_features["UNRATE_change"] = df_features["UNRATE"].diff()

    for t in time_frames:
        df_features[f"UNRATE_t+{t}"] = df_features["UNRATE"].shift(-t)
        df_features[f"UNRATE_t+{t}_change"] = df_features[f"UNRATE_t+{t}"]-df_features["UNRATE"]

    return df_features

if __name__ == "__main__":
    get_all_features()

