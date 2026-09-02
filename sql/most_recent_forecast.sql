SELECT *
FROM Runs
ORDER BY
    strftime('%Y-%m', ForecastTarget) DESC,
    datetime(ExecutionDate) DESC,
    RunID DESC
LIMIT 1;