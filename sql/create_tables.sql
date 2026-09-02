CREATE TABLE IF NOT EXISTS FREDSeries (
SeriesID TEXT PRIMARY KEY,
Title TEXT NOT NULL,
DefaultFrequency TEXT NOT NULL,
Units TEXT NOT NULL,
ObservationStart TEXT NOT NULL,
FRED_LastUpdateLocalTime TEXT NOT NULL,
FRED_LastUpdateUTC TEXT NOT NULL,
CreationDate TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS FREDObservations (
    SeriesID TEXT NOT NULL,
    ObservationDate TEXT NOT NULL,
    NativeValue REAL,
    DateFetched TEXT NOT NULL DEFAULT (datetime('now')),

    PRIMARY KEY (SeriesID, ObservationDate),

    FOREIGN KEY (SeriesID)
        REFERENCES FREDSeries(SeriesID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS MonthlyFeatures (
    SeriesID TEXT NOT NULL,
    MonthYear TEXT NOT NULL,
    MonthlyValue REAL,
    DateCalculated TEXT NOT NULL DEFAULT (datetime('now')),

    PRIMARY KEY (SeriesID, MonthYear),
    FOREIGN KEY (SeriesID)
        REFERENCES FREDSeries(SeriesID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Runs (
    RunID INTEGER PRIMARY KEY,

    EvaluationTrainingStart TEXT NOT NULL,
    EvaluationTrainingEnd TEXT NOT NULL,
    TestStart TEXT NOT NULL,
    TestEnd TEXT NOT NULL,

    Lambda REAL NOT NULL,
    MAEOptimizingWeight REAL NOT NULL,

    ModelMAE REAL NOT NULL,
    NaiveMAE REAL NOT NULL,
    ModelRMSE REAL NOT NULL,
    NaiveRMSE REAL NOT NULL,
    ModelMAEImprovement REAL NOT NULL,
    ModelRMSEImprovement REAL NOT NULL,
    ModelMAPE REAL NOT NULL,
    NaiveMAPE REAL NOT NULL,
    
    ProdModelTrainingStart TEXT NOT NULL,
    ProdModelTrainingEnd TEXT NOT NULL,
    ForecastOrigin TEXT NOT NULL,
    ForecastTarget TEXT NOT NULL,
    ModelForecast REAL NOT NULL,
    NaiveForecast REAL NOT NULL,

    ActualUNRATE REAL,
    ModelAbsError REAL,
    NaiveAbsError REAL,

    ExecutionDate TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS Forecasts (
    ForecastID INTEGER PRIMARY KEY,
    RunID INTEGER NOT NULL,

    EvaluationTrainingStart TEXT NOT NULL,
    EvaluationTrainingEnd TEXT NOT NULL,
    TestStart TEXT NOT NULL,
    TestEnd TEXT NOT NULL,

    Lambda REAL NOT NULL,
    MAEOptimizingWeight REAL NOT NULL,

    ModelMAE REAL NOT NULL,
    NaiveMAE REAL NOT NULL,
    ModelRMSE REAL NOT NULL,
    NaiveRMSE REAL NOT NULL,
    ModelMAEImprovement REAL NOT NULL,
    ModelRMSEImprovement REAL NOT NULL,
    ModelMAPE REAL NOT NULL,
    NaiveMAPE REAL NOT NULL,
    
    ProdModelTrainingStart TEXT NOT NULL,
    ProdModelTrainingEnd TEXT NOT NULL,
    ForecastOrigin TEXT NOT NULL,
    ForecastTarget TEXT NOT NULL,
    ModelForecast REAL NOT NULL,
    NaiveForecast REAL NOT NULL,

    ActualUNRATE REAL,
    ModelAbsError REAL,
    NaiveAbsError REAL,

    ExecutionDate TEXT NOT NULL,

    FOREIGN KEY (RunID)
        REFERENCES Runs(RunID)
        ON DELETE CASCADE
    
    UNIQUE (ForecastTarget)
)   
