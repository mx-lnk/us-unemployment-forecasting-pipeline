UPDATE Forecasts

SET
    ReleaseDateHistorical = r.ReleaseDateHistorical,
    ActualUNRATEHistorical = r.ActualUNRATEHistorical,
    ModelAbsErrorHistorical = r.ModelAbsErrorHistorical,
    NaiveAbsErrorHistorical = r.NaiveAbsErrorHistorical,

    ActualUNRATELive = r.ActualUNRATELive,
    ModelAbsErrorLive = r.ModelAbsErrorLive,
    NaiveAbsErrorLive = r.NaiveAbsErrorLive

FROM Runs AS r

WHERE Forecasts.RunID = r.RunID;