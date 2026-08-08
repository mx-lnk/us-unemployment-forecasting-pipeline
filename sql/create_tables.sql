CREATE TABLE IF NOT EXISTS FREDSeries (
SeriesID TEXT PRIMARY KEY,
Title TEXT NOT NULL,
DefaultFrequency TEXT NOT NULL,
Units TEXT NOT NULL,
ObservationStart TEXT NOT NULL,
FRED_LastUpdateCD TEXT NOT NULL,
FRED_LastUpdateUTC TEXT NOT NULL,
CreationDate TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS FREDObservations (
    SeriesID TEXT NOT NULL,
    ObservationDate TEXT NOT NULL,
    NativeValue REAL NOT NULL,
    DateFetched TEXT NOT NULL DEFAULT (datetime('now')),

    PRIMARY KEY (SeriesID, ObservationDate),

    FOREIGN KEY (SeriesID)
        REFERENCES FREDSeries(SeriesID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS MonthlyFeatures (
    SeriesID TEXT NOT NULL,
    MonthYear TEXT NOT NULL,
    MonthlyValue REAL NOT NULL,
    DateCalculated TEXT NOT NULL DEFAULT (datetime('now')),

    PRIMARY KEY (SeriesID, MonthYear),
    FOREIGN KEY (SeriesID)
        REFERENCES FREDSeries(SeriesID)
        ON DELETE CASCADE
);