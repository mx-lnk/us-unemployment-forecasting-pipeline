import database
import new_obs_checker
import data_pipeline
import feature_pipeline
import model
import ex_ante_forecasts

def init_pipeline(series_ids, feature_set, force_execution = False):

    # --- create db and tables if not existing ---
    database.create_tables()

    # --- check if new observations are available on FRED. If so, kick of the pipeline
    if new_obs_checker.new_obs_available(series_ids) or force_execution:

        # 1) fetch meta data about or series IDs from FRED and UPSERT into the db
        data_pipeline.fred_series_data_pipeline(series_ids)

        # 2) fetch and UPSERT all observations for our series IDs from FRED,
        #    starting from the earliest common observation start date minus one month for t-1 features,
        #    depending on availability.
        data_pipeline.fred_observations_data_pipeline(series_ids)

        # 3) prepare the features and aggregate them into a df, compatible with the model
        df_features = feature_pipeline.get_features()

        # 4) run the model
        df_test_metrics, df_test_results, df_forecast = model.weighted_ridge_regression(
            feature_set=feature_set,
            df=df_features,
            n_lambda_candidates=50,
            n_lambda_optimization_steps=10,
            lower_lambda=1e-6,
            upper_lambda=1e4,
            print_details=False,
            forecast_mode=True,
            backtest_last_origin=None
        )

        # 5) store the forecast and metrics of this run in the Runs table
        model.export_results(df_test_metrics, df_forecast)

        # 6) store the most recent forecast and metrics for the current month in the Forecasts table.
        #    Note that this will UPSERT the db entry only within the current month,
        #    so that the Forecasts table represents is and ex-ante forecasts collection.
        ex_ante_forecasts.aggregate_forecast()

        # 7) UPSERT historical (as they were release in the next period) as well as
        #    up-to-date (including revisions) values for ActualUNRATE, ModelAbsError, and NaiveAbsError.
    else: print("No new obs available")


        

if __name__ == "__main__":
    SERIES_IDS = ['UNRATE', 'INDPRO', 'JTSJOL']
    feature_set = ['log_10_JTSJOL_t-1', 'UNRATE_t', 'INDPRO_t-1']

    init_pipeline(series_ids=SERIES_IDS, feature_set=feature_set, force_execution=True)



