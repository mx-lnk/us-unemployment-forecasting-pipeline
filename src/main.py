import database
import update_checker
import data_pipeline
import feature_pipeline
import model



SERIES_IDS = ['UNRATE', 'PAYEMS', 'ICSA', 'INDPRO', 'JTSJOL']
FINAL_SERIES_IDS = ['UNRATE', 'INDPRO', 'JTSJOL']
feature_set = ['log10_INDPRO', 'log10_JTSJOL', 'log10_UNRATE', 'UNRATE']
model_id = 1



# --- create db and tables if not existing ---
database.create_tables()

# --- check if new data for all IDs of the final selection of series IDs is available, before kicking off the pipeline ---
db_outdated = update_checker.check_db_all_entries_outdated(final_series_ids=FINAL_SERIES_IDS, feature_set=feature_set)
if db_outdated:

    # UPSERT FREDSeries table
    data_pipeline.fred_series_data_pipeline(series_ids=SERIES_IDS)

    # UPSERT all observations for all series IDs starting from the earliest common observations start date
    data_pipeline.fred_observations_data_pipeline(series_ids=SERIES_IDS)

    # turn the previously retrieved observations into monthly features and UPSERT them to the db
    data_pipeline.monthly_features_data_pipeline()

    # retrieve the monthly features from the db, transform, impute them,
    # and turn them into a df, containing the final feature set for the model
    df_features = feature_pipeline.get_feature_selection()

    # run the model and retrieve the results as dfs
    df_test_metrics, df_test_results, df_forecast = model.weighted_ridge_regression(df=df_features,
                                                                                    feature_set=feature_set,
                                                                                    n_lambda_candidates = 50,
                                                                                    n_lambda_optimization_steps = 10,
                                                                                    lower_lambda = 1e-6,
                                                                                    upper_lambda = 1e4,
                                                                                    print_details = False,
                                                                                    forecast_mode = True,
                                                                                    backtest_last_origin = None)

    # insert the results and metrics of the run into the db
    # ------------------------------------------------------------------------------------------------------------------
    # Before uncomment add a final forecast table which contains the most recent execution date of the month as the 
    # final forecast for this month
    # ------------------------------------------------------------------------------------------------------------------
    # model.export_results(df_test_metrics=df_test_metrics, df_forecast=df_forecast, model_id=model_id)

    print(df_forecast)

# else: print("DB is up-to-date")








