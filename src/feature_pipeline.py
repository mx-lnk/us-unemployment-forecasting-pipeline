import numpy as np
import pandas as pd
from pathlib import Path
import database

def get_feature_selection():
    # Fetch all complete months from the db
    data = database.db_requester_fetchall(sql_script="final_selection_MonthlyFeatures.sql")

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
    features = ['INDPRO', 'JTSJOL', 'UNRATE']
    df_imputed = df.copy()
    df_imputed[features] = df[features].interpolate(method="linear")
    df_imputed[df_imputed.isna().any(axis=1)]

    # construct a master df containing all features
    df_features = pd.DataFrame({
        "month_year": df_imputed['month_year'].copy(),
        "log10_INDPRO": df_imputed['INDPRO'].apply(np.log10).copy(),
        "log10_JTSJOL": df_imputed['JTSJOL'].apply(np.log10).copy(),
        "log10_UNRATE": df_imputed['UNRATE'].apply(np.log10).copy(),
        "UNRATE": df_imputed['UNRATE'].copy(),
        "UNRATE_t+1": df_imputed['UNRATE'].shift(-1).copy(),
    })

    return df_features

if __name__ == "__main__":
    get_feature_selection()

