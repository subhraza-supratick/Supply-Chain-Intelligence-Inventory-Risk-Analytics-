"""
Execute key analytical SQL queries directly on the SQLite Data Warehouse (Localized for INR).
Displays clean tabular results for sales trends, stockouts, and supplier rankings in Indian Rupees (INR).
"""

import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "supply_chain.db")

def run_queries():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Run src/run_pipeline.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    pd.set_option('display.max_columns', 15)
    pd.set_option('display.width', 1000)

    print("=" * 85)
    print("LIVE SQL ANALYTICS EXECUTION ON DATA WAREHOUSE (LOCALIZED FOR INDIA & INR)")
    print("=" * 85)

    # Query 1: Executive Financial Summary in INR Crores / Lakhs
    q1 = """
    SELECT
        COUNT(DISTINCT sale_id) AS total_orders,
        SUM(quantity_sold) AS total_units_sold,
        PRINTF('INR %,.2f', SUM(total_revenue)) AS total_revenue_inr,
        PRINTF('INR %,.2f', SUM(total_cogs)) AS total_cogs_inr,
        PRINTF('INR %,.2f', SUM(gross_profit)) AS total_gross_profit_inr,
        ROUND((SUM(gross_profit) / SUM(total_revenue)) * 100, 2) || '%' AS gross_profit_margin
    FROM fact_sales;
    """
    print("\n[KPI 1: Executive Financial Summary (INR)]")
    print(pd.read_sql_query(q1, conn).to_string(index=False))

    # Query 2: Top 5 Best-Selling Products by Revenue
    q2 = """
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        SUM(s.quantity_sold) AS units_sold,
        PRINTF('INR %,.2f', SUM(s.total_revenue)) AS total_revenue,
        ROUND((SUM(s.gross_profit) / SUM(s.total_revenue)) * 100, 2) || '%' AS margin
    FROM fact_sales s
    JOIN dim_product p ON s.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
    ORDER BY SUM(s.total_revenue) DESC
    LIMIT 5;
    """
    print("\n[KPI 2: Top 5 Best-Selling SKUs by Revenue in India]")
    print(pd.read_sql_query(q2, conn).to_string(index=False))

    # Query 3: Critical Inventory Risk Hotspots
    q3 = """
    SELECT
        product_id,
        product_name,
        category,
        warehouse_id,
        current_closing_stock AS current_stock,
        forecast_demand_lead_time AS lead_time_demand,
        days_of_inventory AS doi,
        inventory_risk_score AS risk_score,
        risk_category,
        recommended_action
    FROM analytics_inventory_risk
    WHERE risk_category IN ('Critical', 'High')
    ORDER BY inventory_risk_score DESC
    LIMIT 6;
    """
    print("\n[KPI 3: Critical & High Risk Inventory Hotspots across Indian DCs]")
    print(pd.read_sql_query(q3, conn).to_string(index=False))

    # Query 4: Supplier Performance Scorecard & Risk Ranking
    q4 = """
    SELECT
        supplier_id,
        supplier_name,
        supplier_region,
        on_time_delivery_rate_pct || '%' AS on_time_pct,
        avg_delay_days || ' days' AS avg_delay,
        fill_rate_pct || '%' AS fill_rate,
        defect_rate_pct || '%' AS defect_rate,
        supplier_risk_score,
        supplier_rating
    FROM analytics_supplier_scorecard
    ORDER BY supplier_risk_score DESC
    LIMIT 5;
    """
    print("\n[KPI 4: Bottom 5 Underperforming Indian Suppliers by Risk Index]")
    print(pd.read_sql_query(q4, conn).to_string(index=False))

    print("\n" + "=" * 85)
    conn.close()

if __name__ == "__main__":
    run_queries()
