"""
Train Model Module.
Trains machine learning models for supply chain demand forecasting.
Uses RandomForestRegressor and GradientBoostingRegressor.
"""

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import numpy as np
import pandas as pd

def train_demand_model(X_train, y_train, model_type="random_forest", n_estimators=150, random_state=42):
    """
    Trains and returns a regression model for demand forecasting.
    """
    print(f"Training {model_type.replace('_', ' ').title()} Demand Forecasting Model...")
    
    if model_type == "random_forest":
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=12,
            min_samples_leaf=3,
            n_jobs=-1,
            random_state=random_state
        )
    elif model_type == "gradient_boosting":
        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=6,
            learning_rate=0.08,
            random_state=random_state
        )
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
        
    model.fit(X_train, y_train)
    print(" -> Model fitting completed successfully.")
    return model

def get_feature_importance(model, feature_cols):
    """Returns a sorted DataFrame of feature importances."""
    importances = model.feature_importances_
    df_imp = pd.DataFrame({
        "feature": feature_cols,
        "importance": importances
    }).sort_values(by="importance", ascending=False).reset_index(drop=True)
    df_imp["importance_pct"] = round(df_imp["importance"] * 100, 2)
    return df_imp
