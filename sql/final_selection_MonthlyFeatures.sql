WITH CompleteMonths AS (
    SELECT MonthYear
    FROM MonthlyFeatures
    WHERE SeriesID IN ('UNRATE', 'INDPRO', 'JTSJOL')
    GROUP BY MonthYear
    HAVING COUNT(DISTINCT SeriesID) = 3
),

LatestCompleteMonth AS (
    SELECT MAX(MonthYear) AS MonthYear
    FROM CompleteMonths
)

SELECT
    mf.SeriesID,
    mf.MonthYear,
    mf.MonthlyValue,
    mf.DateCalculated
FROM MonthlyFeatures AS mf
WHERE mf.SeriesID IN ('UNRATE', 'INDPRO', 'JTSJOL')
  AND mf.MonthYear <= (
      SELECT MonthYear
      FROM LatestCompleteMonth
  )
ORDER BY
    mf.MonthYear,
    mf.SeriesID;