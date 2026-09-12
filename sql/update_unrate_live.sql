UPDATE Runs
SET ActualUNRATELive = FREDObservations.NativeValue
FROM FREDObservations
WHERE Runs.ForecastTarget = substr(FREDObservations.ObservationDate, 1,7)