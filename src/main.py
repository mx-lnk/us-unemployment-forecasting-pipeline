import database
import update_checker
import data_pipeline
import feature_pipeline
import model
import ex_ante_forecasts



def init_pipeline(series_ids, final_series_ids, feature_set, force_execution):
        
    # --- create db and tables if not existing ---
    database.create_tables()

    # --- check if new data for all IDs of the final selection of series IDs is available, before kicking off the pipeline ---
    db_outdated = update_checker.check_db_all_entries_outdated(final_series_ids=final_series_ids, feature_set=feature_set)
    if db_outdated or force_execution:

        # fetch and UPSERT FREDSeries table
        data_pipeline.fred_series_data_pipeline(series_ids=series_ids)

        # fetch and UPSERT all observations for all series IDs starting from the earliest common observations start date
        data_pipeline.fred_observations_data_pipeline(series_ids=series_ids)

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
        model.export_results(df_test_metrics=df_test_metrics, df_forecast=df_forecast)

        # UPSERTs the most recent forecast for the current month into the Forecasts table,
        # to build up over time a collection of ex-ante forecasts.
        ex_ante_forecasts.aggregate_forecast()

        # ------------------------------------------------------------------------------------------------------------------
        # Add an if / else statement, which checks if the updated data has resulted in a new forecast
        # or was only a revision done by the FED. If its a new forecast add to the previous forecast the ActualUNRATE
        # and calculate the NaiveAbsError and ModelAbsError
        #
        # How to identify if re-running the pipeline has resulted in a new forecast??
        # Probably if a the most and second latest month have both ActualUNRATE = NULL, then even with multiple entries,
        # this should work but we need to figure out how to aggregate this in SQLite
        #
        # Or just check, if for the most recent entry of column ForecastTarget in Runs table,
        # if the FRED has already posted an UNRATE value to the month year of our most recent ForecastTarget
        #
        # If new UNRATE data is published, the entries for ActualUNRATE, NaiveAbsError, and ModelAbsError must be UPDATED in 
        # tables Runs and Forecasts for the regarding month
        #
        # Get the newly published UNRATE value from the MonthlyFeatures table,
        # which will be update when reaching this point in the code.
        # The SQLite query should also update all UNRATEs in our Runs and Forecasts table
        # to accommodate potential revisions by matching the ForecastTarget date with the MonthYear column
        # ------------------------------------------------------------------------------------------------------------------

    # else: print("DB is up-to-date")


if __name__ == "__main__":
    SERIES_IDS = ['UNRATE', 'PAYEMS', 'ICSA', 'INDPRO', 'JTSJOL']
    FINAL_SERIES_IDS = ['UNRATE', 'INDPRO', 'JTSJOL']
    feature_set = ['log10_INDPRO', 'log10_JTSJOL', 'log10_UNRATE', 'UNRATE']

    init_pipeline(SERIES_IDS, FINAL_SERIES_IDS, feature_set, force_execution=True)



