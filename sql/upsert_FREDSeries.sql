INSERT INTO FREDSeries (
    SeriesID,
    Title,
    DefaultFrequency,
    Units,
    ObservationStart,
    FRED_LastUpdateLocalTime,
    FRED_LastUpdateUTC
)
VALUES (
    :series_id,
    :title,
    :frequency,
    :units,
    :observation_start,
    :last_update_local_time,
    :last_update_utc
)

ON CONFLICT(SeriesID) DO UPDATE SET
    Title = excluded.Title,
    DefaultFrequency = excluded.DefaultFrequency,
    Units = excluded.Units,
    ObservationStart = excluded.ObservationStart,
    FRED_LastUpdateLocalTime = excluded.FRED_LastUpdateLocalTime,
    FRED_LastUpdateUTC = excluded.FRED_LastUpdateUTC;