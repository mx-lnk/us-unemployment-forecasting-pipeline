SELECT *
FROM Runs
ORDER BY
    ForecastTarget DESC,
    datetime(ExecutionDate) DESC,
    RunID DESC
LIMIT 1;