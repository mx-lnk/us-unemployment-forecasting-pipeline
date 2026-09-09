INSERT INTO Runs (
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
    NaiveAbsErrorLive
)

VALUES (
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
    :UNRATE_forecast,
    :naive_forecast,

    :release_date_historical,
    :actual_unrate_historical,
    :model_abs_error_historical,
    :naive_abs_error_historical,
    
    :actual_unrate_live,
    :model_abs_error_live,
    :naive_abs_error_live
);