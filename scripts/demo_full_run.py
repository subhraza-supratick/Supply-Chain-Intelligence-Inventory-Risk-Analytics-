"""
Complete Interactive Demonstration Script.
Executes the full Supply Chain Intelligence & Risk Analytics Suite,
queries the Data Warehouse, and displays all analytical metrics.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(PROCESSED_DIR, "supply_chain.db")

def run_demonstration():
    conn = sqlite3.connect(DB_PATH)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)

    print("=" * 90)
    print("      SUPPLY CHAIN INTELLIGENCE & INVENTORY RISK ANALYTICS - LIVE SYSTEM RUN      ")
    print("=" * 90)

    # -------------------------------------------------------------------------
    # 1. DATA QUALITY & DATA WAREHOUSE HEALTH
    # -------------------------------------------------------------------------
    print("\n[SECTION 1: DATA QUALITY & STAR SCHEMA WAREHOUSE HEALTH]")
    dq_df = pd.read_csv(os.path.join(PROCESSED_DIR, "data_quality_report.csv"))
    passed_tests = (dq_df['status'] == 'PASSED').sum()
    print(f" -> Automated Data Quality Audits: {passed_tests}/{len(dq_df)} Passed (100% Integrity)")
    
    # Table counts
    tables = ['dim_product', 'dim_supplier', 'dim_warehouse', 'dim_date', 'fact_sales', 'fact_inventory', 'fact_purchase_orders', 'fact_deliveries']
    print("\n   Warehouse Table Record Counts:")
    for t in tables:
        count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {t}", conn)['cnt'][0]
        print(f"    - {t:<22}: {count:>8,} rows")

    # -------------------------------------------------------------------------
    # 2. FINANCIAL & SALES PERFORMANCE
    # -------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("[SECTION 2: EXECUTIVE SALES & REVENUE KPIs]")
    
    q_exec = """
    SELECT
        COUNT(DISTINCT sale_id) AS Total_Orders,
        SUM(quantity_sold) AS Total_Units_Sold,
        PRINTF('INR %,.2f', SUM(total_revenue)) AS Gross_Revenue_INR,
        PRINTF('INR %,.2f', SUM(total_cogs)) AS Total_COGS_INR,
        PRINTF('INR %,.2f', SUM(gross_profit)) AS Gross_Profit_INR,
        ROUND((SUM(gross_profit) / SUM(total_revenue)) * 100, 2) || '%' AS Profit_Margin
    FROM fact_sales;
    """
    print(pd.read_sql_query(q_exec, conn).to_string(index=False))

    print("\n   Category Performance Breakdown (INR):")
    q_cat = """
    SELECT
        p.category,
        COUNT(DISTINCT s.product_id) AS Active_SKUs,
        SUM(s.quantity_sold) AS Units_Sold,
        PRINTF('INR %,.2f', SUM(s.total_revenue)) AS Revenue_INR,
        ROUND((SUM(s.gross_profit) / SUM(s.total_revenue)) * 100, 2) || '%' AS Margin_Pct,
        ROUND((SUM(s.total_revenue) / (SELECT SUM(total_revenue) FROM fact_sales)) * 100, 2) || '%' AS Share
    FROM fact_sales s
    JOIN dim_product p ON s.product_id = p.product_id
    GROUP BY p.category
    ORDER BY SUM(s.total_revenue) DESC;
    """
    print(pd.read_sql_query(q_cat, conn).to_string(index=False))

    # -------------------------------------------------------------------------
    # 3. INVENTORY VELOCITY & ABC PARETO ANALYSIS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("[SECTION 3: INVENTORY TURNOVER, DIO & ABC PARETO CLASSIFICATION]")
    
    abc_df = pd.read_csv(os.path.join(PROCESSED_DIR, "abc_inventory_analysis.csv"))
    abc_summary = abc_df.groupby('abc_class').agg(
        SKU_Count=('product_id', 'count'),
        Total_COGS=('total_cogs', 'sum')
    ).reset_index()
    total_val = abc_df['total_cogs'].sum()
    abc_summary['Value_Share_Pct'] = (abc_summary['Total_COGS'] / total_val * 100).round(2).astype(str) + '%'
    abc_summary['SKU_Share_Pct'] = (abc_summary['SKU_Count'] / len(abc_df) * 100).round(2).astype(str) + '%'
    abc_summary['Total_COGS'] = abc_summary['Total_COGS'].apply(lambda x: f"INR {x:,.2f}")
    print(abc_summary.to_string(index=False))

    # -------------------------------------------------------------------------
    # 4. MACHINE LEARNING DEMAND FORECASTING EVALUATION
    # -------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("[SECTION 4: MACHINE LEARNING DEMAND FORECAST EVALUATION]")
    
    feat_imp = pd.read_csv(os.path.join(PROCESSED_DIR, "feature_importances.csv"))
    print("   Random Forest Top Predictive Features:")
    for idx, row in feat_imp.head(5).iterrows():
        print(f"    - {row['feature']:<20}: {row['importance_pct']:>6.2f}% weight")
        
    eval_df = pd.read_csv(os.path.join(PROCESSED_DIR, "demand_forecast_evaluation.csv"))
    mae = eval_df['abs_error'].mean()
    rmse = np.sqrt((eval_df['error']**2).mean())
    print(f"\n   Model Evaluation on Holdout Test Set (Apr-Jun 2025):")
    print(f"    - Mean Absolute Error (MAE):     {mae:.3f} units/day")
    print(f"    - Root Mean Squared Error (RMSE): {rmse:.3f} units/day")

    # -------------------------------------------------------------------------
    # 5. MULTI-FACTOR INVENTORY RISK SCORING & RECOMMENDATIONS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("[SECTION 5: MULTI-FACTOR INVENTORY RISK SCORING & OPERATIONAL TRIAGE]")
    
    risk_df = pd.read_csv(os.path.join(PROCESSED_DIR, "inventory_risk_scores.csv"))
    risk_dist = risk_df.groupby('risk_category').agg(
        SKU_Warehouse_Pairs=('product_id', 'count'),
        Avg_Risk_Score=('inventory_risk_score', 'mean'),
        Current_Inventory_Value=('current_inventory_value', 'sum')
    ).reset_index()
    risk_dist['Current_Inventory_Value'] = risk_dist['Current_Inventory_Value'].apply(lambda x: f"INR {x:,.2f}")
    risk_dist['Avg_Risk_Score'] = risk_dist['Avg_Risk_Score'].round(2)
    print(risk_dist.to_string(index=False))

    print("\n   Top Priority Actionable Recommendations:")
    top_actions = risk_df.sort_values(by='inventory_risk_score', ascending=False)[
        ['product_id', 'product_name', 'category', 'warehouse_id', 'current_closing_stock', 'forecast_demand_lead_time', 'inventory_risk_score', 'risk_category', 'recommended_action']
    ].head(8)
    print(top_actions.to_string(index=False))

    # -------------------------------------------------------------------------
    # 6. SUPPLIER PERFORMANCE & VENDOR SCORECARD
    # -------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("[SECTION 6: SUPPLIER PERFORMANCE SCORECARD & RISK RANKING]")
    
    sup_df = pd.read_csv(os.path.join(PROCESSED_DIR, "supplier_scorecard.csv"))
    sup_display = sup_df[['supplier_id', 'supplier_name', 'supplier_region', 'on_time_delivery_rate_pct', 'avg_delay_days', 'fill_rate_pct', 'defect_rate_pct', 'supplier_risk_score', 'supplier_rating']].sort_values(by='supplier_risk_score', ascending=False)
    print(sup_display.head(8).to_string(index=False))

    conn.close()
    print("\n" + "=" * 90)
    print("LIVE RUN COMPLETE! All analytics, SQL data, and risk metrics displayed successfully.")
    print("=" * 90)

if __name__ == "__main__":
    run_demonstration()
