INSERT INTO FREDSeries (
    SeriesID,
    Title,
    DefaultFrequency,
    Units,
    ObservationStart,
    ObservationEnd,
    FREDLastUpdateLocalTime,
    FREDLastUpdateUTC
)
VALUES (
    :series_id,
    :title,
    :frequency,
    :units,
    :observation_start,
    :observation_end,
    :last_update_local_time,
    :last_update_utc
)

ON CONFLICT(SeriesID) DO UPDATE SET
    Title = excluded.Title,
    DefaultFrequency = excluded.DefaultFrequency,
    Units = excluded.Units,
    ObservationStart = excluded.ObservationStart,
    ObservationEnd = excluded.ObservationEnd,
    FREDLastUpdateLocalTime = excluded.FREDLastUpdateLocalTime,
    FREDLastUpdateUTC = excluded.FREDLastUpdateUTC;