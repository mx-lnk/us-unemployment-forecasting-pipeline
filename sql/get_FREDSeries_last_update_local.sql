SELECT SeriesID, FRED_LastUpdateLocalTime FROM FREDSeries
WHERE SeriesID IN ({placeholder_ids})