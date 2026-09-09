INSERT INTO Forecasts (
    RunID,

    EvaluationTrainingStart,
    EvaluationTrainingEnd,
    TestStart,
    TestEnd,

    Lambda,
    MAEOptimizingWeight,

    ModelMAE,
    NaiveMAE,
    ModelRMSE,
    NaiveRMSE,
    ModelMAEImprovement,
    ModelRMSEImprovement,
    ModelMAPE,
    NaiveMAPE,

    ProdModelTrainingStart,
    ProdModelTrainingEnd,
    ForecastOrigin,
    ForecastTarget,
    ModelForecast,
    NaiveForecast,

    ReleaseDateHistorical,
    ActualUNRATEHistorical,
    ModelAbsErrorHistorical,
    NaiveAbsErrorHistorical,

    ActualUNRATELive,
    ModelAbsErrorLive,
    NaiveAbsErrorLive,

    ExecutionDate
)
VALUES (
    :run_id,

    :evaluation_training_start,
    :evaluation_training_end,
    :test_start,
    :test_end,

    :lambda,
    :mae_optimizing_weight,

    :model_mae,
    :naive_mae,
    :model_rmse,
    :naive_rmse,
    :model_mae_improvement,
    :model_rmse_improvement,
    :model_mape,
    :naive_mape,
    
    :production_model_training_start,
    :production_model_training_end,
    :forecast_origin_t,
    :forecast_target_t1,
    :model_forecast,
    :naive_forecast,

    :release_date_historical,
    :actual_unrate_historical,
    :model_abs_error_historical,
    :naive_abs_error_historical,
    
    :actual_unrate_live,
    :model_abs_error_live,
    :naive_abs_error_live,

    :execution_date
)

ON CONFLICT(ForecastTarget) DO UPDATE SET
    RunID = excluded.RunID,

    EvaluationTrainingStart = excluded.EvaluationTrainingStart,
    EvaluationTrainingEnd = excluded.EvaluationTrainingEnd,
    TestStart = excluded.TestStart,
    TestEnd = excluded.TestEnd,

    Lambda = excluded.Lambda,
    MAEOptimizingWeight = excluded.MAEOptimizingWeight,

    ModelMAE = excluded.ModelMAE,
    NaiveMAE = excluded.NaiveMAE,
    ModelRMSE = excluded.ModelRMSE,
    NaiveRMSE = excluded.NaiveRMSE,
    ModelMAEImprovement = excluded.ModelMAEImprovement,
    ModelRMSEImprovement = excluded.ModelRMSEImprovement,
    ModelMAPE = excluded.ModelMAPE,
    NaiveMAPE = excluded.NaiveMAPE,

    ProdModelTrainingStart = excluded.ProdModelTrainingStart,
    ProdModelTrainingEnd = excluded.ProdModelTrainingEnd,
    ForecastOrigin = excluded.ForecastOrigin,
    ForecastTarget = excluded.ForecastTarget,
    ModelForecast = excluded.ModelForecast,
    NaiveForecast = excluded.NaiveForecast,

    ReleaseDateHistorical = excluded.ReleaseDateHistorical,
    ActualUNRATEHistorical = excluded.ActualUNRATEHistorical,
    ModelAbsErrorHistorical = excluded.ModelAbsErrorHistorical,
    NaiveAbsErrorHistorical = excluded.NaiveAbsErrorHistorical,
    
    ActualUNRATELive = excluded.ActualUNRATELive,
    ModelAbsErrorLive = excluded.ModelAbsErrorLive,
    NaiveAbsErrorLive = excluded.NaiveAbsErrorLive,

    ExecutionDate = excluded.ExecutionDate;
