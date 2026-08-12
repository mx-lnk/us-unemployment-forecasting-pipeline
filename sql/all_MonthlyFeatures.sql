-- SELECT * FROM MonthlyFeatures;

WITH LatestCompleteMonth AS (
    SELECT mf.MonthYear
    FROM MonthlyFeatures mf
    GROUP BY mf.MonthYear
    HAVING COUNT(DISTINCT mf.SeriesID) = (
        SELECT COUNT(*)
        FROM FREDSeries
    )
    ORDER BY mf.MonthYear DESC
    LIMIT 1
)
SELECT mf.*
FROM MonthlyFeatures mf
WHERE mf.MonthYear <= (
    SELECT MonthYear
    FROM LatestCompleteMonth
)
ORDER BY mf.MonthYear, mf.SeriesID;