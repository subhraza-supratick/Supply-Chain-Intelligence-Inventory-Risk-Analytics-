"""
Feature Engineering for Demand Forecasting.
Creates time-series lag and rolling window features for product-warehouse level demand:
- Lag features: lag_1, lag_7, lag_14, lag_28
- Rolling statistics: rolling_mean_7, rolling_mean_14, rolling_mean_28, rolling_std_7
- Calendar features: month, day_of_week, quarter, day_of_year, is_weekend
- Chronological train/test split (prevents data leakage).
"""

import pandas as pd
import numpy as np

def build_demand_features(fact_sales, target_products=None):
    """
    Constructs daily time-series demand dataset and engineers lag/rolling features.
    If target_products is None, processes the top volume products or all active products.
    """
    print("Building Demand Time-Series Features...")
    
    # 1. Daily aggregation by product and warehouse
    daily_demand = fact_sales.groupby(["sale_date", "product_id", "warehouse_id"])["quantity_sold"].sum().reset_index()
    daily_demand["sale_date"] = pd.to_datetime(daily_demand["sale_date"])
    
    # Select target cohort for forecasting (e.g. top 50 high-velocity products or all specified)
    if target_products is not None:
        daily_demand = daily_demand[daily_demand["product_id"].isin(target_products)]
    else:
        top_prods = fact_sales.groupby("product_id")["quantity_sold"].sum().nlargest(60).index.tolist()
        daily_demand = daily_demand[daily_demand["product_id"].isin(top_prods)]
        
    # Reindex to create continuous daily calendar per product-warehouse series (filling zero-demand days)
    unique_dates = pd.date_range(daily_demand["sale_date"].min(), daily_demand["sale_date"].max(), freq="D")
    unique_series = daily_demand[["product_id", "warehouse_id"]].drop_duplicates()
    
    full_grid = []
    for _, row in unique_series.iterrows():
        grid = pd.DataFrame({"sale_date": unique_dates})
        grid["product_id"] = row["product_id"]
        grid["warehouse_id"] = row["warehouse_id"]
        full_grid.append(grid)
        
    df_grid = pd.concat(full_grid, ignore_index=True)
    df_merged = pd.merge(df_grid, daily_demand, on=["sale_date", "product_id", "warehouse_id"], how="left")
    df_merged["quantity_sold"] = df_merged["quantity_sold"].fillna(0)
    
    # Sort chronologically within each product-warehouse series
    df_merged = df_merged.sort_values(by=["product_id", "warehouse_id", "sale_date"]).reset_index(drop=True)
    
    # 2. Lag Features
    for lag in [1, 7, 14, 28]:
        df_merged[f"lag_{lag}"] = df_merged.groupby(["product_id", "warehouse_id"])["quantity_sold"].shift(lag)
        
    # 3. Rolling Window Features (shifted by 1 to avoid data leakage)
    for window in [7, 14, 28]:
        df_merged[f"rolling_mean_{window}"] = df_merged.groupby(["product_id", "warehouse_id"])["quantity_sold"].shift(1).rolling(window=window, min_periods=1).mean()
        
    df_merged["rolling_std_7"] = df_merged.groupby(["product_id", "warehouse_id"])["quantity_sold"].shift(1).rolling(window=7, min_periods=1).std().fillna(0)
    
    # 4. Calendar Features
    df_merged["month"] = df_merged["sale_date"].dt.month
    df_merged["day_of_week"] = df_merged["sale_date"].dt.weekday
    df_merged["quarter"] = df_merged["sale_date"].dt.quarter
    df_merged["day_of_year"] = df_merged["sale_date"].dt.dayofyear
    df_merged["is_weekend"] = df_merged["day_of_week"].isin([5, 6]).astype(int)
    
    # Drop initial rows with NaN from 28-day lag
    df_clean = df_merged.dropna().reset_index(drop=True)
    print(f" -> Constructed {len(df_clean):,} feature records across {df_clean['product_id'].nunique()} products")
    return df_clean

def split_chronological(df_features, split_date="2024-10-01"):
    """
    Performs a strict chronological train/test split.
    Training: Dates < split_date (e.g. Jan 2024 - Mar 2025)
    Testing: Dates >= split_date (e.g. Apr 2025 - Jun 2025 holdout)
    """
    feature_cols = [
        "lag_1", "lag_7", "lag_14", "lag_28",
        "rolling_mean_7", "rolling_mean_14", "rolling_mean_28", "rolling_std_7",
        "month", "day_of_week", "quarter", "day_of_year", "is_weekend"
    ]
    target_col = "quantity_sold"
    
    train_mask = df_features["sale_date"] < pd.to_datetime(split_date)
    test_mask = df_features["sale_date"] >= pd.to_datetime(split_date)
    
    train_df = df_features[train_mask]
    test_df = df_features[test_mask]
    
    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]
    
    print(f"Chronological Split: Training set = {len(train_df):,} samples | Test set = {len(test_df):,} samples")
    return X_train, y_train, X_test, y_test, train_df, test_df, feature_cols
