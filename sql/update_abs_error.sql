UPDATE Runs
SET 
    ModelAbsErrorHistorical = abs(ModelForecast - ActualUNRATEHistorical),
    NaiveAbsErrorHistorical = abs(NaiveForecast - ActualUNRATEHistorical)
WHERE ActualUNRATEHistorical IS NOT NULL;

UPDATE Runs
SET
    ModelAbsErrorLive = abs(ModelForecast - ActualUNRATELive),
    NaiveAbsErrorLive = abs(NaiveForecast - ActualUNRATELive)
WHERE ActualUNRATELive IS NOT NULL;