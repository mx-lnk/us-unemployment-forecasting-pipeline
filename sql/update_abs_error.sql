UPDATE Runs
SET 
    ModelAbsErrorHistorical = abs(ModelForecast - ActualUNRATEHistorical),
    NaiveAbsErrorHistorical = abs(NaiveForecast - ActualUNRATEHistorical),

    ModelAbsErrorLive = abs(ModelForecast - ActualUNRATELive),
    NaiveAbsErrorLive = abs(NaiveForecast - ActualUNRATELive)

WHERE ActualUNRATEHistorical IS NOT NULL
    AND ActualUNRATELive IS NOT NULL;