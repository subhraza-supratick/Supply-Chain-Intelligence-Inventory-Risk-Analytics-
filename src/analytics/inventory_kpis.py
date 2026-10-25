"""
Inventory KPIs & ABC Analysis Module.
Calculates core supply chain metrics:
- Cost of Goods Sold (COGS)
- Average Inventory & Inventory Turnover Ratio
- Days Inventory Outstanding (DIO)
- Stock-out Rate (%)
- Days of Inventory (DOI)
- Excess / Slow-Moving Inventory Identification
- ABC Inventory Classification (Pareto 80/15/5 analysis)
"""

import os
import pandas as pd
import numpy as np

def calculate_inventory_kpis(fact_sales, fact_inventory, dim_product, fact_deliveries=None):
    """
    Computes product-level and warehouse-level inventory KPIs.
    """
    print("Computing Inventory KPIs...")
    
    # 1. Total Units Sold and Sales Revenue per Product-Warehouse
    sales_summary = fact_sales.groupby(["product_id", "warehouse_id"]).agg(
        total_units_sold=("quantity_sold", "sum"),
        total_revenue=("total_revenue", "sum"),
        total_cogs=("total_cogs", "sum"),
        active_sales_days=("sale_date", "nunique")
    ).reset_index()
    
    # Daily demand estimate
    total_calendar_days = fact_sales["sale_date"].nunique()
    sales_summary["avg_daily_demand"] = round(sales_summary["total_units_sold"] / max(1, total_calendar_days), 3)
    
    # 2. Inventory Metrics per Product-Warehouse
    inv_summary = fact_inventory.groupby(["product_id", "warehouse_id"]).agg(
        total_inventory_snapshots=("inventory_date", "count"),
        stockout_days=("is_stockout", "sum"),
        avg_closing_stock=("closing_stock", "mean"),
        current_closing_stock=("closing_stock", "last"), # latest recorded snapshot
        avg_inventory_value=("closing_inventory_value", "mean"),
        current_inventory_value=("closing_inventory_value", "last")
    ).reset_index()
    
    # Stock-out Rate
    inv_summary["stockout_rate_pct"] = round(
        (inv_summary["stockout_days"] / inv_summary["total_inventory_snapshots"]) * 100, 2
    )
    
    # Merge Sales & Inventory
    kpi_df = pd.merge(sales_summary, inv_summary, on=["product_id", "warehouse_id"], how="outer").fillna(0)
    
    # Merge Product metadata (lead time, unit cost, safety stock, reorder point)
    prod_meta = dim_product[["product_id", "product_name", "category", "subcategory", "unit_cost", "selling_price", "lead_time_days", "safety_stock", "reorder_point"]]
    kpi_df = pd.merge(kpi_df, prod_meta, on="product_id", how="left")
    
    # 3. Inventory Turnover & Days Inventory Outstanding (DIO)
    # Annualized COGS factor (if 18 months / 546 days: multiply by 365 / 546)
    annual_factor = 365.0 / max(1, total_calendar_days)
    kpi_df["annualized_cogs"] = kpi_df["total_cogs"] * annual_factor
    kpi_df["annual_units_sold"] = kpi_df["total_units_sold"] * annual_factor
    
    # Inventory Turnover = COGS / Average Inventory Value
    kpi_df["inventory_turnover"] = np.where(
        kpi_df["avg_inventory_value"] > 0,
        np.round(kpi_df["annualized_cogs"] / kpi_df["avg_inventory_value"], 2),
        0.0
    )
    
    # Days Inventory Outstanding (DIO) = (Average Inventory Value / COGS) * 365
    kpi_df["dio_days"] = np.where(
        kpi_df["annualized_cogs"] > 0,
        np.round((kpi_df["avg_inventory_value"] / kpi_df["annualized_cogs"]) * 365, 1),
        999.0
    )
    
    # 4. Days of Inventory (DOI) based on current stock
    kpi_df["days_of_inventory"] = np.where(
        kpi_df["avg_daily_demand"] > 0,
        np.round(kpi_df["current_closing_stock"] / kpi_df["avg_daily_demand"], 1),
        999.0
    )
    
    # 5. Target Inventory and Excess Inventory Calculation
    # Target Inventory = (Average Daily Demand * Lead Time) + Safety Stock
    kpi_df["demand_during_lead_time"] = round(kpi_df["avg_daily_demand"] * kpi_df["lead_time_days"], 1)
    kpi_df["target_inventory"] = np.ceil(kpi_df["demand_during_lead_time"] + kpi_df["safety_stock"]).astype(int)
    
    # Excess Stock = Current Stock - Target Inventory (if positive)
    kpi_df["excess_units"] = np.maximum(0, kpi_df["current_closing_stock"] - kpi_df["target_inventory"])
    kpi_df["excess_inventory_value"] = round(kpi_df["excess_units"] * kpi_df["unit_cost"], 2)
    
    # Slow Moving Flag (> 120 days of inventory)
    kpi_df["is_slow_moving"] = (kpi_df["days_of_inventory"] > 120).astype(int)
    
    # Inventory Health Status
    conditions = [
        (kpi_df["current_closing_stock"] <= 0),
        (kpi_df["current_closing_stock"] < kpi_df["safety_stock"]),
        (kpi_df["days_of_inventory"] > 120) | (kpi_df["excess_units"] > kpi_df["target_inventory"] * 1.5),
    ]
    choices = ["Stock-out", "Low Stock / Understocked", "Excess / Overstocked"]
    kpi_df["inventory_health_status"] = np.select(conditions, choices, default="Healthy")
    
    return kpi_df

def perform_abc_analysis(fact_sales, dim_product):
    """
    Performs Pareto ABC Analysis based on Annual Consumption Value (Annual Units Sold * Unit Cost).
    - Class A: Top ~80% of consumption value
    - Class B: Next ~15% of consumption value (80% - 95%)
    - Class C: Remaining ~5% of consumption value (95% - 100%)
    """
    print("Performing Pareto ABC Inventory Classification...")
    sales_by_prod = fact_sales.groupby("product_id").agg(
        total_units_sold=("quantity_sold", "sum"),
        total_cogs=("total_cogs", "sum")
    ).reset_index()
    
    df_abc = pd.merge(dim_product, sales_by_prod, on="product_id", how="left").fillna(0)
    
    # Sort by Consumption Value descending
    df_abc = df_abc.sort_values(by="total_cogs", ascending=False).reset_index(drop=True)
    
    # Cumulative consumption value and percentages
    total_val = df_abc["total_cogs"].sum()
    df_abc["cum_cogs"] = df_abc["total_cogs"].cumsum()
    df_abc["cum_cogs_pct"] = (df_abc["cum_cogs"] / total_val) * 100
    df_abc["cum_product_pct"] = ((df_abc.index + 1) / len(df_abc)) * 100
    
    # Assign ABC Category
    def assign_abc(cum_pct):
        if cum_pct <= 80.0:
            return "A"
        elif cum_pct <= 95.0:
            return "B"
        else:
            return "C"
            
    df_abc["abc_class"] = df_abc["cum_cogs_pct"].apply(assign_abc)
    
    # Summary stats
    summary = df_abc.groupby("abc_class").agg(
        product_count=("product_id", "count"),
        total_cogs_value=("total_cogs", "sum")
    ).reset_index()
    summary["pct_of_total_value"] = round(summary["total_cogs_value"] / total_val * 100, 2)
    summary["pct_of_total_skus"] = round(summary["product_count"] / len(df_abc) * 100, 2)
    
    print("\nABC Classification Summary:")
    print(summary.to_string(index=False))
    
    return df_abc[["product_id", "product_name", "category", "unit_cost", "total_units_sold", "total_cogs", "cum_cogs_pct", "abc_class"]]
