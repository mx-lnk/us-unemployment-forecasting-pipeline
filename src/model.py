import numpy as np
import pandas as pd
from pathlib import Path
import database
import feature_pipeline

# --- The model ---
def weighted_ridge_regression(feature_set,
                              df,
                              n_lambda_candidates = 50,
                              n_lambda_optimization_steps = 10,
                              lower_lambda = 1e-6,
                              upper_lambda = 1e4,
                              print_details = False,
                              forecast_mode = False,
                              backtest_last_origin = None):
    # zero-variance guard
    def zero_variance_guard(std_values):
        if np.any(np.isclose(std_values, 0)):
            raise ValueError("At least one feature has zero or near-zero standard deviation.")

    # if a backtesting end date is given, create a date-capped df
    if backtest_last_origin:
        if forecast_mode:
            raise Exception(f"In backtesting mode, no forecasts can be produced!")

        backtest_last_origin = pd.Period(backtest_last_origin, freq='M')

        if backtest_last_origin >= df['year_month_t'].max():
            raise Exception(f"Your last origin backtest date has to be before the most recent observation date ({df['year_month_t'].max()})!")
        
        df = df[df['year_month_t'] <= (backtest_last_origin)].copy()

        if len(df) < 10 * len(feature_set):
            raise Exception(f"For your back test end date are not enough observations available!\nPlease choose a end date beyond {(df['year_month_t'].min() + 10 * len(feature_set)) - 1}")

        print(f"BACKTEST MODE ENABLED")
        
    # split data into training, validation, test, and target
    target = "UNRATE_t+1"
    cols = ['year_month_t'] + feature_set + ['UNRATE_t', target]
    cols = list(dict.fromkeys(cols))

    df_tvt = df[cols].dropna().copy() # tvt -> training, validation, and testing

    set_len = len(df_tvt)
    
    # in chronological order form df_tvt: 60% training and optimizing lambda and MAE weighting,
    # 60% -> 80% validation, retrain up to 80%, test against last 20% (80% -> 100%)
    train_end = int(round(set_len*0.6))
    val_end = int(round(set_len*0.8))

    X_train = df_tvt[feature_set].iloc[:train_end].to_numpy()
    X_val = df_tvt[feature_set].iloc[train_end:val_end].to_numpy()
    X_train_full = df_tvt[feature_set].iloc[:val_end].to_numpy()
    X_test = df_tvt[feature_set].iloc[val_end:].to_numpy()

    y_train = df_tvt[target].iloc[:train_end].to_numpy()
    y_val = df_tvt[target].iloc[train_end:val_end].to_numpy()
    y_train_full = df_tvt[target].iloc[:val_end].to_numpy()
    y_test = df_tvt[target].iloc[val_end:].to_numpy()

    y_pred_naive_val = df_tvt['UNRATE_t'].iloc[train_end:val_end].to_numpy()
    y_pred_naive_test = df_tvt['UNRATE_t'].iloc[val_end:].to_numpy()

    # standardize via z-score X and centering y
    def standardizing_X_centering_y(X_train, X_input, y_train):
        X_train_mean = X_train.mean(axis=0)
        X_train_std = X_train.std(axis=0)
        zero_variance_guard(X_train_std)

        Z_train = (X_train - X_train_mean) / X_train_std
        Z_input = (X_input - X_train_mean) / X_train_std

        y_train_mean = y_train.mean()

        y_train_centered = y_train - y_train_mean

        return Z_train, Z_input, y_train_mean, y_train_centered

    # fit model
    def fit_model(Z_train, Z_input, y_train_centered, y_train_mean, penalty_param, mae_w, y_pred_naive):
        A = Z_train.T @ Z_train + penalty_param * np.eye(Z_train.shape[1])
        b = Z_train.T @ y_train_centered

        beta_coeffs = np.linalg.solve(A, b)

        y_pred_raw = y_train_mean + Z_input @ beta_coeffs
        y_pred = mae_w * y_pred_raw + (1 - mae_w) * y_pred_naive

        return y_pred

    # find best lambda (penalty_param)
    # actual lambda values, not exponents -> np.geomspace is logspace for non-exponent values
    best_penalty_param = None
    best_val_rmse = np.inf

    Z_train, Z_val, y_train_mean, y_train_centered = standardizing_X_centering_y(X_train=X_train, X_input=X_val, y_train=y_train)

    for step in range(n_lambda_optimization_steps):
        lambda_space = np.geomspace(
            lower_lambda,
            upper_lambda,
            n_lambda_candidates
        )

        rmse_values = np.empty(len(lambda_space))

        for i, penalty_param in enumerate(lambda_space):
            y_pred_val = fit_model(
                Z_train=Z_train,
                Z_input=Z_val,
                y_train_centered=y_train_centered,
                y_train_mean=y_train_mean,
                penalty_param=penalty_param,
                mae_w=1,
                y_pred_naive=1
            )

            rmse = np.sqrt(np.mean((y_val - y_pred_val) ** 2))
            rmse_values[i] = rmse
        

        # pos of best lambda in current search
        best_pos = np.argmin(rmse_values)

        step_best_penalty_param = lambda_space[best_pos]
        step_best_rmse = rmse_values[best_pos]

        # store best result found overall
        if step_best_rmse < best_val_rmse:
            best_val_rmse = step_best_rmse
            best_penalty_param = step_best_penalty_param

        # refine around the best lambda
        lower_pos = max(best_pos - 1, 0)
        upper_pos = min(best_pos + 1, len(lambda_space) - 1)

        lower_lambda = lambda_space[lower_pos]
        upper_lambda = lambda_space[upper_pos]

        if print_details:
            print(
                f"Step {step + 1}: "
                f"lambda={step_best_penalty_param:.6f}, "
                f"validation RMSE={step_best_rmse:.6f}"
            )

    # refit training model with best lambda (penalty_param)
    y_pred_val = fit_model(
        Z_train=Z_train,
        Z_input=Z_val,
        y_train_centered=y_train_centered,
        y_train_mean=y_train_mean,
        penalty_param=best_penalty_param,
        mae_w=1,
        y_pred_naive=1
    )

    # find a weighting for optimal MAE due to strong performance of naive model
    weight_candidates = np.linspace(0, 1, 101)

    best_mae_w = None
    best_weighted_val_mae = np.inf

    for weight in weight_candidates:

        y_pred_val_weighted = (weight * y_pred_val + (1 - weight) * y_pred_naive_val)

        weighted_val_mae = np.mean(np.abs(y_val - y_pred_val_weighted))

        if weighted_val_mae < best_weighted_val_mae:
            best_weighted_val_mae = weighted_val_mae
            best_mae_w = weight


    # refit model on 80%
    Z_train_full, Z_test, y_train_full_mean, y_train_full_centered = standardizing_X_centering_y(X_train_full, X_test, y_train_full)

    y_pred_test = fit_model(Z_train_full,
                            Z_test,
                            y_train_full_centered,
                            y_train_full_mean,
                            best_penalty_param,
                            best_mae_w,
                            y_pred_naive_test)
    
    # --- TEST METRICS ---

    # MAE in pp
    model_mae = np.mean(np.abs(y_test - y_pred_test))
    naive_mae = np.mean(np.abs(y_test - y_pred_naive_test))

    # RMSE in pp
    model_rmse = np.sqrt(np.mean((y_test - y_pred_test) ** 2))
    naive_rmse = np.sqrt(np.mean((y_test - y_pred_naive_test) ** 2))

    # MAPE in %
    model_mape = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
    naive_mape = np.mean(np.abs((y_test - y_pred_naive_test) / y_test)) * 100

    # model over Naive improvement in %
    if naive_mae == 0:
        model_mae_improvement = np.nan
    else:
        model_mae_improvement = (1 - (model_mae / naive_mae)) * 100
    if naive_rmse == 0:
        model_rmse_improvement = np.nan
    else:
        model_rmse_improvement = (1 - (model_rmse / naive_rmse)) * 100

    df_test_metrics = pd.DataFrame([{
        "evaluation_training_start": df_tvt['year_month_t'].iloc[0],
        "evaluation_training_end": df_tvt['year_month_t'].iloc[val_end - 1],
        "test_start": df_tvt['year_month_t'].iloc[val_end],
        "test_end": df_tvt['year_month_t'].iloc[-1],
        "lambda": best_penalty_param,
        "mae_optimizing_weight": best_mae_w,
        "model_mae": model_mae,
        "naive_mae": naive_mae,
        "model_rmse": model_rmse,
        "naive_rmse": naive_rmse,
        "model_mae_improvement": model_mae_improvement,
        "model_rmse_improvement": model_rmse_improvement,
        "model_mape": model_mape,
        "naive_mape": naive_mape
    }])

    # --- TEST RESULTS ---

    df_test_results = pd.DataFrame({
        "forecast_origin_t": df_tvt['year_month_t'].iloc[val_end:].copy(),
        "forecast_target_t+1": df_tvt['year_month_t'].iloc[val_end:].copy() + 1,
        "UNRATE_t+1": y_test,
        "y_pred_model_t+1": y_pred_test,
        "y_pred_naive_t+1": y_pred_naive_test,
        "model_abs_error": np.abs(y_test - y_pred_test),
        "naive_abs_error": np.abs(y_test - y_pred_naive_test),
    }).reset_index(drop=True)

    # --- FORECAST MODE ---
    df_forecast = None

    if forecast_mode:
        # use all available data
        final_train_cols = ['year_month_t'] + feature_set + [target]
        final_train_cols = list(dict.fromkeys(final_train_cols))

        forecast_cols = (['year_month_t'] + feature_set + ['UNRATE_t'])
        forecast_cols = list(dict.fromkeys(forecast_cols))

        df_final_train = df[final_train_cols].dropna().copy()
        df_forecast_input = df[forecast_cols].dropna().tail(1).copy()

        X_final_train = df_final_train[feature_set].to_numpy()
        y_final_train = df_final_train[target].to_numpy()

        X_forecast_input = df_forecast_input[feature_set].to_numpy()
        y_forecast_naive = df_forecast_input['UNRATE_t'].to_numpy()

        Z_final_train, Z_forecast, y_final_train_mean, y_final_train_centered = standardizing_X_centering_y(X_final_train,
                                                                                                            X_forecast_input,
                                                                                                            y_final_train)

        y_forecast = fit_model(Z_final_train,
                               Z_forecast,
                               y_final_train_centered,
                               y_final_train_mean,
                               best_penalty_param,
                               best_mae_w,
                               y_forecast_naive)

        df_forecast = pd.DataFrame({
            "production_model_training_start": df_final_train['year_month_t'].iloc[0],
            "production_model_training_end": df_final_train['year_month_t'].iloc[-1],
            "forecast_origin_t": df_forecast_input['year_month_t'].to_numpy(),
            "forecast_target_t+1": (df_forecast_input['year_month_t'] + 1).to_numpy(),
            "lambda": best_penalty_param,
            "mae_optimizing_weight": best_mae_w,
            "UNRATE_forecast": y_forecast,
            "naive_forecast": y_forecast_naive
        })

    return df_test_metrics, df_test_results, df_forecast    



# --- Export results from model to db ---
def export_results (df_test_metrics, df_forecast):

    # prepare a combined dict for writing to Runs
    combined_df = pd.concat([df_test_metrics.drop(columns=['lambda', 'mae_optimizing_weight']).reset_index(drop=True), df_forecast.reset_index(drop=True)], axis=1)
    combined_dict = combined_df.to_dict(orient='records')[0]
    combined_dict.update({
        "release_date_historical": None,
        "actual_unrate_historical": None,
        "model_abs_error_historical": None,
        "naive_abs_error_historical": None,

        "actual_unrate_live": None,
        "model_abs_error_live": None,
        "naive_abs_error_live": None
    })

    # convert dtypes period and np.float/.int into sqlite compatible datatypes
    for key, value in combined_dict.items():
        if isinstance(value, pd.Period):
            combined_dict[key] = str(value)
        elif isinstance(value, np.generic):
            combined_dict[key] = value.item()

    combined_dict['forecast_target_t1'] = combined_dict.pop('forecast_target_t+1')

    # write to dict to Runs 
    # execute many expects a list, hence wrap the dict into one
    database.db_upsert_insert_many(sql_script="insert_Runs.sql", data=[combined_dict])


if __name__ == "__main__":
    df_features = feature_pipeline.get_features()
    feature_set = ['log_10_JTSJOL_t-1', 'UNRATE_t', 'INDPRO_t-1']

    df_test_metrics, df_test_results, df_forecast = weighted_ridge_regression(df=df_features, feature_set=feature_set, forecast_mode=True)
    print(df_forecast)
    # export_results(df_test_metrics, df_forecast)