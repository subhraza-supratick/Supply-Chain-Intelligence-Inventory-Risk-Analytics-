"""
Export all processed data into a single structured JSON file for the standalone interactive dashboard (India & INR Localized).
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
os.makedirs(DASHBOARD_DIR, exist_ok=True)

def export_dashboard_data():
    print("Exporting data for the Interactive Web Dashboard (INR Localized)...")
    
    # 1. Executive Summary
    sales_df = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_sales.csv"))
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
    
    total_revenue = float(sales_df['total_revenue'].sum())
    total_cogs = float(sales_df['total_cogs'].sum())
    gross_profit = float(sales_df['gross_profit'].sum())
    profit_margin = round((gross_profit / total_revenue) * 100, 2)
    total_orders = int(sales_df['sale_id'].nunique())
    total_units_sold = int(sales_df['quantity_sold'].sum())
    
    # Monthly sales trend in INR Crores (1 Crore = 10,000,000 INR)
    monthly = sales_df.set_index('sale_date').resample('ME').agg(
        revenue=('total_revenue', 'sum'),
        cogs=('total_cogs', 'sum'),
        profit=('gross_profit', 'sum')
    ).reset_index()
    
    monthly_trend = {
        "labels": monthly['sale_date'].dt.strftime('%b %Y').tolist(),
        "revenue": (monthly['revenue'] / 1e7).round(2).tolist(), # INR Crores
        "cogs": (monthly['cogs'] / 1e7).round(2).tolist(),
        "profit": (monthly['profit'] / 1e7).round(2).tolist(),
    }
    
    # Category sales breakdown in INR Crores
    prod_df = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_product.csv"))
    cat_sales = sales_df.groupby('product_id').agg(
        revenue=('total_revenue', 'sum'),
        units=('quantity_sold', 'sum')
    ).reset_index()
    cat_merged = pd.merge(cat_sales, prod_df[['product_id', 'category']], on='product_id')
    cat_summary = cat_merged.groupby('category')['revenue'].sum().reset_index()
    category_breakdown = {
        "labels": cat_summary['category'].tolist(),
        "data": (cat_summary['revenue'] / 1e7).round(2).tolist() # INR Crores
    }
    
    # Warehouse fulfillment in INR Crores
    wh_df = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_warehouse.csv"))
    wh_sales = sales_df.groupby('warehouse_id')['total_revenue'].sum().reset_index()
    wh_merged = pd.merge(wh_sales, wh_df, on='warehouse_id')
    warehouse_breakdown = {
        "labels": wh_merged['city'].tolist(),
        "data": (wh_merged['total_revenue'] / 1e7).round(2).tolist() # INR Crores
    }
    
    # 2. Inventory Risk & Health
    risk_df = pd.read_csv(os.path.join(PROCESSED_DIR, "inventory_risk_scores.csv"))
    
    risk_counts = risk_df['risk_category'].value_counts().to_dict()
    health_counts = risk_df['inventory_health_status'].value_counts().to_dict()
    
    risk_records = risk_df[[
        'product_id', 'product_name', 'category', 'warehouse_id',
        'current_closing_stock', 'forecast_demand_lead_time', 'days_of_inventory',
        'current_inventory_value', 'inventory_risk_score', 'risk_category',
        'recommended_action', 'abc_class'
    ]].to_dict(orient='records')
    
    # 3. Demand Forecasting
    feat_imp = pd.read_csv(os.path.join(PROCESSED_DIR, "feature_importances.csv"))
    feature_importance_data = {
        "labels": feat_imp['feature'].tolist(),
        "data": feat_imp['importance_pct'].round(2).tolist()
    }
    
    eval_df = pd.read_csv(os.path.join(PROCESSED_DIR, "demand_forecast_evaluation.csv"))
    mae = round(float(eval_df['abs_error'].mean()), 3)
    rmse = round(float(np.sqrt((eval_df['error']**2).mean())), 3)
    
    sample_sku = eval_df['product_id'].iloc[0]
    sample_df = eval_df[(eval_df['product_id'] == sample_sku) & (eval_df['warehouse_id'] == 'W001')].sort_values('sale_date')
    forecast_comparison = {
        "sku": sample_sku,
        "dates": sample_df['sale_date'].tolist(),
        "actual": sample_df['quantity_sold'].tolist(),
        "predicted": sample_df['predicted_demand'].round(1).tolist()
    }
    
    # 4. Supplier Scorecards
    sup_df = pd.read_csv(os.path.join(PROCESSED_DIR, "supplier_scorecard.csv"))
    supplier_records = sup_df[[
        'supplier_id', 'supplier_name', 'supplier_region', 'supplier_type',
        'on_time_delivery_rate_pct', 'avg_delay_days', 'fill_rate_pct',
        'defect_rate_pct', 'total_procurement_spend', 'supplier_risk_score', 'supplier_rating'
    ]].to_dict(orient='records')
    
    dashboard_data = {
        "executive": {
            "total_revenue": total_revenue,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "profit_margin": profit_margin,
            "total_orders": total_orders,
            "total_units_sold": total_units_sold,
            "monthly_trend": monthly_trend,
            "category_breakdown": category_breakdown,
            "warehouse_breakdown": warehouse_breakdown,
            "health_counts": health_counts
        },
        "inventory": {
            "risk_counts": risk_counts,
            "health_counts": health_counts,
            "total_inventory_value": float(risk_df['current_inventory_value'].sum()),
            "excess_inventory_value": float(risk_df['excess_inventory_value'].sum()),
            "critical_count": int((risk_df['risk_category'] == 'Critical').sum()),
            "high_count": int((risk_df['risk_category'] == 'High').sum()),
            "stockout_count": int((risk_df['current_closing_stock'] <= 0).sum()),
            "records": risk_records
        },
        "forecasting": {
            "mae": mae,
            "rmse": rmse,
            "feature_importance": feature_importance_data,
            "sample_comparison": forecast_comparison
        },
        "suppliers": {
            "avg_otd": round(float(sup_df['on_time_delivery_rate_pct'].mean()), 2),
            "avg_delay": round(float(sup_df['avg_delay_days'].mean()), 2),
            "avg_fill_rate": round(float(sup_df['fill_rate_pct'].mean()), 2),
            "avg_defect_rate": round(float(sup_df['defect_rate_pct'].mean()), 2),
            "records": supplier_records
        }
    }
    
    out_file = os.path.join(DASHBOARD_DIR, "dashboard_data.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2)
    print(f" -> Exported dashboard JSON to {out_file}")

if __name__ == "__main__":
    export_dashboard_data()
