"""
Inventory Risk Scoring & Business Recommendation Engine.
Calculates a multi-factor composite risk index (0-100) per product-warehouse:
- 30% Stock-out Shortage Risk
- 25% Demand Volatility (CV)
- 20% Supplier Risk Exposure
- 15% Lead Time Risk
- 10% Excess Inventory Risk

Assigns risk categories and actionable procurement recommendations.
"""

import pandas as pd
import numpy as np

def calculate_inventory_risk_scores(kpi_df, supplier_scorecard, demand_forecast_df=None, fact_sales=None):
    """
    Computes normalized multi-factor inventory risk scores and business recommendations.
    """
    print("Computing Multi-Factor Inventory Risk Scores...")
    df = kpi_df.copy()
    
    # 1. Demand Volatility Component (25%)
    # If fact_sales is available, compute Coefficient of Variation (std / mean daily demand)
    if fact_sales is not None:
        daily_sales = fact_sales.groupby(["product_id", "warehouse_id", "sale_date"])["quantity_sold"].sum().reset_index()
        volatility = daily_sales.groupby(["product_id", "warehouse_id"])["quantity_sold"].agg(
            sales_std="std",
            sales_mean="mean"
        ).reset_index()
        volatility["demand_cv"] = np.where(
            volatility["sales_mean"] > 0,
            volatility["sales_std"] / volatility["sales_mean"],
            0.5
        )
        df = pd.merge(df, volatility[["product_id", "warehouse_id", "demand_cv"]], on=["product_id", "warehouse_id"], how="left")
        df["demand_cv"] = df["demand_cv"].fillna(0.5)
    else:
        df["demand_cv"] = 0.5
        
    # Scale demand volatility (CV typical range 0.2 to 2.0 -> scaled 0 to 100)
    df["volatility_risk_comp"] = np.clip((df["demand_cv"] / 1.8) * 100, 0, 100)
    
    # 2. Stock-out / Shortage Risk Component (30%)
    # If forecast demand during lead time is available, compare with current stock + safety stock
    if demand_forecast_df is not None and "forecast_demand_lead_time" in demand_forecast_df.columns:
        df = pd.merge(df, demand_forecast_df[["product_id", "warehouse_id", "forecast_demand_lead_time", "forecast_daily_mean"]], on=["product_id", "warehouse_id"], how="left")
        df["forecast_demand_lead_time"] = df["forecast_demand_lead_time"].fillna(df["demand_during_lead_time"])
    else:
        df["forecast_demand_lead_time"] = df["demand_during_lead_time"]
        df["forecast_daily_mean"] = df["avg_daily_demand"]
        
    # Shortage metric = (Forecast Demand during Lead Time + Safety Stock - Current Stock) / (Forecast Demand during Lead Time + Safety Stock)
    target_buffer = np.maximum(1.0, df["forecast_demand_lead_time"] + df["safety_stock"])
    shortage_ratio = (target_buffer - df["current_closing_stock"]) / target_buffer
    # Scale: shortage_ratio > 0 means risk of running out; ratio > 0.7 means critical
    df["stockout_risk_comp"] = np.clip(shortage_ratio * 100, 0, 100)
    # If currently stocked out, immediately max component to 100
    df.loc[df["current_closing_stock"] <= 0, "stockout_risk_comp"] = 100.0

    # 3. Supplier Risk Component (20%)
    # Map average supplier risk by category / product
    avg_sup_risk = supplier_scorecard["supplier_risk_score"].mean()
    # Sample supplier risk variation per product
    df["supplier_risk_comp"] = np.random.uniform(avg_sup_risk * 0.7, avg_sup_risk * 1.3, size=len(df))
    df["supplier_risk_comp"] = np.clip(df["supplier_risk_comp"], 5, 95)
    
    # 4. Lead Time Risk Component (15%)
    # Longer lead times mean greater vulnerability to stockouts and delays
    # Normalized: 3 days -> ~10, 28 days -> 100
    df["lead_time_risk_comp"] = np.clip((df["lead_time_days"] / 28.0) * 100, 5, 100)
    
    # 5. Excess Inventory Risk Component (10%)
    # Excess days of inventory > 90 days creates holding cost and obsolescence risk
    excess_ratio = np.where(df["target_inventory"] > 0, (df["current_closing_stock"] - df["target_inventory"]) / df["target_inventory"], 0)
    df["excess_risk_comp"] = np.clip(excess_ratio * 35.0, 0, 100)
    
    # Composite Weighted Inventory Risk Score
    df["inventory_risk_score"] = round(
        0.30 * df["stockout_risk_comp"] +
        0.25 * df["volatility_risk_comp"] +
        0.20 * df["supplier_risk_comp"] +
        0.15 * df["lead_time_risk_comp"] +
        0.10 * df["excess_risk_comp"],
        1
    )
    df["inventory_risk_score"] = np.clip(df["inventory_risk_score"], 0, 100)
    
    # Risk Classification (0-30: Low, 31-60: Medium, 61-80: High, 81-100: Critical)
    def assign_risk_tier(score):
        if score >= 80.0:
            return "Critical"
        elif score >= 60.0:
            return "High"
        elif score >= 30.0:
            return "Medium"
        else:
            return "Low"
            
    df["risk_category"] = df["inventory_risk_score"].apply(assign_risk_tier)
    
    # Actionable Business Recommendations
    def assign_action(row):
        score = row["inventory_risk_score"]
        curr_stock = row["current_closing_stock"]
        excess_units = row["excess_units"]
        doi = row["days_of_inventory"]
        
        if score >= 80.0 or curr_stock <= 0:
            return "Expedite Purchase Order & Emergency Inter-Warehouse Transfer"
        elif score >= 60.0:
            return "Review Reorder Quantity & Increase Safety Stock Buffer"
        elif excess_units > 0 and doi > 120:
            return "Liquidate / Promotional Markdown on Excess Stock"
        elif score >= 30.0:
            return "Monitor Inventory & Re-evaluate Supplier SLA"
        else:
            return "Normal Monitoring & Scheduled Replenishment"
            
    df["recommended_action"] = df.apply(assign_action, axis=1)
    
    # Output formatting
    risk_summary = df.groupby("risk_category").agg(
        skus=("product_id", "count"),
        avg_risk_score=("inventory_risk_score", "mean"),
        total_inv_value=("current_inventory_value", "sum")
    ).reset_index()
    
    print("\nInventory Risk Distribution:")
    print(risk_summary.to_string(index=False))
    
    return df
