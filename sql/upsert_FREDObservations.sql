INSERT INTO FREDObservations (
    SeriesID,
    ObservationDate,
    NativeValue
)

VALUES (
    :series_id,
    :observation_date,
    :native_value
)

ON CONFLICT(SeriesID, ObservationDate) DO UPDATE SET
    NativeValue = excluded.NativeValue,
    DateFetched = CURRENT_TIMESTAMP;