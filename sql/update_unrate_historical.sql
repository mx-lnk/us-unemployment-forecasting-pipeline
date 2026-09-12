UPDATE Runs
SET
    ReleaseDateHistorical = :release_date_historical,
    ActualUNRATEHistorical = :actual_unrate_historical
WHERE ForecastTarget = :forecast_target_t1;