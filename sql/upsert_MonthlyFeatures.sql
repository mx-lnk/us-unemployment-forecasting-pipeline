INSERT INTO MonthlyFeatures (
    SeriesID,
    MonthYear,
    MonthlyValue
)

VALUES (
    :series_id,
    :month_year,
    :monthly_value
)

ON CONFLICT (SeriesID, MonthYear) DO UPDATE SET
    MonthlyValue = excluded.MonthlyValue,
    DateCalculated = CURRENT_TIMESTAMP;
