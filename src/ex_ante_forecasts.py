import database

def aggregate_forecast():

    # will only select the mos recent MonthYear and its most recent ExecutionDate
    mrf = database.db_requester_fetchall(sql_script="most_recent_run.sql")
    dict_keys = [
        "run_id",
        "evaluation_training_start",
        "evaluation_training_end",
        "test_start",
        "test_end",
        "lambda",
        "mae_optimizing_weight",
        "model_mae",
        "naive_mae",
        "model_rmse",
        "naive_rmse",
        "model_mae_improvement",
        "model_rmse_improvement",
        "model_mape",
        "naive_mape",
        "production_model_training_start",
        "production_model_training_end",
        "forecast_origin_t",
        "forecast_target_t1",
        "model_forecast",
        "naive_forecast",
        "release_date_historical",
        "actual_unrate_historical",
        "model_abs_error_historical",
        "naive_abs_error_historical",
        "actual_unrate_live",
        "model_abs_error_live",
        "naive_abs_error_live",
        "execution_date"
    ]
    mrf_dict = dict(zip(dict_keys, mrf[0]))

    # UPSERTs only the current most recent MonthYear, so that the Forecasts table stays ex-ante
    database.db_upsert_insert_many(sql_script="upsert_forecast.sql", data=[mrf_dict])

if __name__ == "__main__":
    aggregate_forecast()