import database
import new_obs_checker
import data_pipeline
import feature_pipeline
import model
import ex_ante_forecasts
import update_actuals
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

handler = RotatingFileHandler(
    LOG_DIR / f"main_pipeline.log",
    maxBytes=1_000_000,
    backupCount=3
)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s",
                    handlers=[handler])

logger = logging.getLogger(__name__)

def init_pipeline(series_ids, feature_set, force_execution = False):

    # --- create db and tables if not existing ---
    database.create_tables()
    logger.info("Database initialized.")

    # --- check if new observations are available on FRED. If so, kick of the pipeline
    if new_obs_checker.new_obs_available(series_ids) or force_execution:
        if force_execution:
            logger.info("Pipeline execution forced.")
        else:
            logger.info("New observations available on FRED -> Pipeline execution started.")

        # 1) fetch meta data about or series IDs from FRED and UPSERT into the db
        logger.info("Updating database with FRED data.")
        data_pipeline.fred_series_data_pipeline(series_ids)

        # 2) fetch and UPSERT all observations for our series IDs from FRED,
        #    starting from the earliest common observation start date minus one month for t-1 features,
        #    depending on availability.
        data_pipeline.fred_observations_data_pipeline(series_ids)

        # 3) prepare the features and aggregate them into a df, compatible with the model
        logger.info("Building feature set.")
        df_features = feature_pipeline.get_features()

        # 4) run the model
        logger.info("Running forecasting model.")
        df_test_metrics, df_test_results, df_forecast = model.ridge_naive_ensemble(
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
        logger.info("Storing results.")
        model.export_results(df_test_metrics, df_forecast)

        # 6) store the most recent forecast and metrics for the current month in the Forecasts table.
        #    Note that this will UPSERT the db entry only within the current month,
        #    so that the Forecasts table represents is and ex-ante forecasts collection.
        logger.info("Storing ex-ante forecast.")
        ex_ante_forecasts.aggregate_forecast()

        # 7) UPDATE Runs and Forecasts tables with historical (as they were release in the next period) as well as
        #    up-to-date (including revisions) values for ActualUNRATE, ModelAbsError, and NaiveAbsError.
        logger.info("Updating actual values.")
        update_actuals.updater()

        logger.info("Pipeline successfully completed.")

    else: 
        logger.info("No new complete set of observations available on FRED -> Pipeline skipped.")


        

if __name__ == "__main__":
    SERIES_IDS = ['UNRATE', 'INDPRO', 'JTSJOL']
    FEATURE_SET = ['log_10_JTSJOL_t-1', 'UNRATE_t', 'INDPRO_t-1']

    try:
        init_pipeline(series_ids=SERIES_IDS, feature_set=FEATURE_SET, force_execution=False)

    except Exception:
        logger.exception("Pipeline failed!")
        raise




