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

    ActualUNRATE,
    ModelAbsError,
    NaiveAbsError
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
    :forecast_origin,
    :forecast_target,
    :model_forecast,
    :naive_forecast,

    :actual_unrate,
    :model_abs_error,
    :naive_abs_error
);