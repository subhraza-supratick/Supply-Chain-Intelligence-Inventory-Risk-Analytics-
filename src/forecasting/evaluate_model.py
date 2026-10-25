"""
Evaluate Model Module.
Evaluates demand forecasting predictions using industry-standard statistical metrics:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- MAPE (Mean Absolute Percentage Error)
- R-squared (R2 Score)

Generates test set comparison reports and future multi-week demand forecasts.
"""

import os
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.etl.load_data import PROCESSED_DATA_DIR

def evaluate_forecasts(y_true, y_pred):
    """
    Computes statistical evaluation metrics for demand predictions.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # Safe MAPE avoiding division by zero
    non_zero_mask = y_true > 0
    if non_zero_mask.sum() > 0:
        mape = np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100
    else:
        mape = 0.0
        
    metrics = {
        "MAE": round(float(mae), 3),
        "RMSE": round(float(rmse), 3),
        "MAPE_pct": round(float(mape), 2),
        "R2_Score": round(float(r2), 4)
    }
    
    print("\n" + "=" * 50)
    print("DEMAND FORECAST MODEL EVALUATION METRICS:")
    print("=" * 50)
    print(f" Mean Absolute Error (MAE):         {metrics['MAE']} units/day")
    print(f" Root Mean Squared Error (RMSE):     {metrics['RMSE']} units/day")
    print(f" Mean Absolute % Error (MAPE):      {metrics['MAPE_pct']}%")
    print(f" Coefficient of Determination (R2): {metrics['R2_Score']}")
    print("=" * 50)
    
    return metrics

def generate_forecast_export(model, test_df, X_test, dim_product, output_dir=PROCESSED_DATA_DIR):
    """
    Generates actual vs predicted comparison dataset and multi-week aggregated forecast by product-warehouse.
    """
    test_eval = test_df.copy()
    test_eval["predicted_demand"] = np.maximum(0, np.round(model.predict(X_test), 2))
    test_eval["error"] = test_eval["predicted_demand"] - test_eval["quantity_sold"]
    test_eval["abs_error"] = np.abs(test_eval["error"])
    
    # Export test actuals vs predictions
    eval_file = os.path.join(output_dir, "demand_forecast_evaluation.csv")
    test_eval[["sale_date", "product_id", "warehouse_id", "quantity_sold", "predicted_demand", "error", "abs_error"]].to_csv(eval_file, index=False)
    print(f" -> Saved detailed forecast evaluation to {eval_file}")
    
    # Aggregate future demand projection by product-warehouse (next 30 days)
    lead_time_map = dim_product.set_index("product_id")["lead_time_days"].to_dict()
    
    forecast_agg = test_eval.groupby(["product_id", "warehouse_id"]).agg(
        forecast_daily_mean=("predicted_demand", "mean"),
        forecast_daily_std=("predicted_demand", "std"),
        actual_daily_mean=("quantity_sold", "mean"),
        test_days_count=("sale_date", "count")
    ).reset_index()
    
    forecast_agg["lead_time_days"] = forecast_agg["product_id"].map(lead_time_map).fillna(7).astype(int)
    forecast_agg["forecast_demand_lead_time"] = round(forecast_agg["forecast_daily_mean"] * forecast_agg["lead_time_days"], 1)
    forecast_agg["forecast_next_30d"] = round(forecast_agg["forecast_daily_mean"] * 30, 1)
    
    forecast_file = os.path.join(output_dir, "demand_forecasts.csv")
    forecast_agg.to_csv(forecast_file, index=False)
    print(f" -> Saved product-warehouse demand forecast projections to {forecast_file}")
    
    return test_eval, forecast_agg
