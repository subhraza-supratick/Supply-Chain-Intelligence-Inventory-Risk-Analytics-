"""
Transform Data Module.
Constructs the Star Schema Data Warehouse tables:
- Dimensions: dim_product, dim_supplier, dim_warehouse, dim_date
- Facts: fact_sales, fact_inventory, fact_purchase_orders, fact_deliveries
Performs feature calculations, margin computations, delivery performance attributes, and stores
the processed datasets ready for SQL querying and Power BI ingestion.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.etl.load_data import PROCESSED_DATA_DIR, get_db_engine, save_to_db

def build_dim_date(start_date="2024-01-01", end_date="2025-12-31"):
    """
    Generates a comprehensive enterprise Date Dimension table.
    """
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    date_range = pd.date_range(start, end, freq="D")
    
    df_date = pd.DataFrame({"full_date": date_range})
    df_date["date_id"] = df_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    df_date["date"] = df_date["full_date"].dt.strftime("%Y-%m-%d")
    df_date["year"] = df_date["full_date"].dt.year
    df_date["quarter"] = df_date["full_date"].dt.quarter
    df_date["quarter_name"] = "Q" + df_date["quarter"].astype(str)
    df_date["year_quarter"] = df_date["year"].astype(str) + "-Q" + df_date["quarter"].astype(str)
    df_date["month"] = df_date["full_date"].dt.month
    df_date["month_name"] = df_date["full_date"].dt.strftime("%B")
    df_date["year_month"] = df_date["full_date"].dt.strftime("%Y-%m")
    df_date["week_of_year"] = df_date["full_date"].dt.isocalendar().week.astype(int)
    df_date["day_of_month"] = df_date["full_date"].dt.day
    df_date["day_of_week"] = df_date["full_date"].dt.weekday # 0=Mon, 6=Sun
    df_date["day_name"] = df_date["full_date"].dt.strftime("%A")
    df_date["is_weekend"] = df_date["day_of_week"].isin([5, 6]).astype(int)
    df_date["is_quarter_end"] = df_date["full_date"].dt.is_quarter_end.astype(int)
    
    df_date = df_date.drop(columns=["full_date"])
    return df_date

def build_dim_product(df_products):
    """Transforms products into dim_product."""
    df = df_products.copy()
    df["gross_margin_pct"] = round((df["selling_price"] - df["unit_cost"]) / df["selling_price"] * 100, 2)
    return df

def build_dim_supplier(df_suppliers):
    """Transforms suppliers into dim_supplier."""
    df = df_suppliers.copy()
    if "contract_start_date" in df.columns:
        df["contract_start_date"] = pd.to_datetime(df["contract_start_date"]).dt.strftime("%Y-%m-%d")
    return df

def build_dim_warehouse(df_warehouses):
    """Transforms warehouses into dim_warehouse."""
    return df_warehouses.copy()

def build_fact_sales(df_sales, df_products):
    """Transforms sales transactions into fact_sales with cost and profit measures."""
    df = df_sales.copy()
    cost_map = df_products.set_index("product_id")["unit_cost"].to_dict()
    
    df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.strftime("%Y-%m-%d")
    df["unit_cost"] = df["product_id"].map(cost_map)
    df["total_revenue"] = round(df["quantity_sold"] * df["unit_price"], 2)
    df["total_cogs"] = round(df["quantity_sold"] * df["unit_cost"], 2)
    df["gross_profit"] = round(df["total_revenue"] - df["total_cogs"], 2)
    df["profit_margin_pct"] = round((df["gross_profit"] / df["total_revenue"]) * 100, 2)
    
    cols = ["sale_id", "sale_date", "product_id", "warehouse_id", "quantity_sold", "unit_price", "unit_cost", "total_revenue", "total_cogs", "gross_profit", "profit_margin_pct", "customer_type", "sales_channel"]
    return df[cols]

def build_fact_inventory(df_inventory, df_products):
    """Transforms inventory snapshot records with valuation and stockout flags."""
    df = df_inventory.copy()
    cost_map = df_products.set_index("product_id")["unit_cost"].to_dict()
    
    df["inventory_date"] = pd.to_datetime(df["inventory_date"]).dt.strftime("%Y-%m-%d")
    df["unit_cost"] = df["product_id"].map(cost_map)
    df["closing_inventory_value"] = round(df["closing_stock"] * df["unit_cost"], 2)
    df["is_stockout"] = (df["closing_stock"] <= 0).astype(int)
    
    cols = ["inventory_date", "product_id", "warehouse_id", "opening_stock", "stock_received", "quantity_sold", "damaged_stock", "closing_stock", "unit_cost", "closing_inventory_value", "is_stockout"]
    return df[cols]

def build_fact_purchase_orders(df_po):
    """Transforms purchase orders into fact_purchase_orders."""
    df = df_po.copy()
    
    po_dt = pd.to_datetime(df["po_date"])
    exp_dt = pd.to_datetime(df["expected_delivery_date"])
    act_dt = pd.to_datetime(df["actual_delivery_date"])
    
    df["po_date"] = po_dt.dt.strftime("%Y-%m-%d")
    df["expected_delivery_date"] = exp_dt.dt.strftime("%Y-%m-%d")
    df["actual_delivery_date"] = act_dt.dt.strftime("%Y-%m-%d")
    
    df["total_po_cost"] = round(df["ordered_quantity"] * df["unit_cost"], 2)
    df["target_lead_time_days"] = (exp_dt - po_dt).dt.days
    df["actual_lead_time_days"] = (act_dt - po_dt).dt.days
    df["delay_days"] = (act_dt - exp_dt).dt.days
    df["is_delayed"] = (df["delay_days"] > 0).astype(int)
    
    cols = ["po_id", "po_date", "supplier_id", "product_id", "warehouse_id", "ordered_quantity", "expected_delivery_date", "actual_delivery_date", "unit_cost", "total_po_cost", "target_lead_time_days", "actual_lead_time_days", "delay_days", "is_delayed"]
    return df[cols]

def build_fact_deliveries(df_deliveries):
    """Transforms delivery logs into fact_deliveries with SLA KPIs."""
    df = df_deliveries.copy()
    
    disp_dt = pd.to_datetime(df["dispatch_date"])
    exp_dt = pd.to_datetime(df["expected_delivery_date"])
    act_dt = pd.to_datetime(df["actual_delivery_date"])
    
    df["dispatch_date"] = disp_dt.dt.strftime("%Y-%m-%d")
    df["expected_delivery_date"] = exp_dt.dt.strftime("%Y-%m-%d")
    df["actual_delivery_date"] = act_dt.dt.strftime("%Y-%m-%d")
    
    df["transit_days"] = (act_dt - disp_dt).dt.days
    df["delay_days"] = (act_dt - exp_dt).dt.days
    df["is_on_time"] = (df["delay_days"] <= 0).astype(int)
    
    # Fill rate & Defect rate
    df["fill_rate_pct"] = np.round(np.where(df["quantity_ordered"] > 0, (df["quantity_received"] / df["quantity_ordered"]) * 100, 100.0), 2)
    df["defect_rate_pct"] = np.round(np.where(df["quantity_received"] > 0, (df["damaged_quantity"] / df["quantity_received"]) * 100, 0.0), 2)
    
    cols = ["delivery_id", "po_id", "supplier_id", "product_id", "warehouse_id", "dispatch_date", "expected_delivery_date", "actual_delivery_date", "quantity_ordered", "quantity_received", "damaged_quantity", "transit_days", "delay_days", "is_on_time", "fill_rate_pct", "defect_rate_pct"]
    return df[cols]

def transform_all_data(cleaned_data_dict):
    """
    Constructs all Star Schema Dimension and Fact tables, exports to CSV, and loads into database.
    """
    print("=" * 70)
    print("TRANSFORMING DATA INTO STAR SCHEMA WAREHOUSE TABLES...")
    print("=" * 70)
    
    dim_date = build_dim_date()
    dim_product = build_dim_product(cleaned_data_dict["products"])
    dim_supplier = build_dim_supplier(cleaned_data_dict["suppliers"])
    dim_warehouse = build_dim_warehouse(cleaned_data_dict["warehouses"])
    
    fact_sales = build_fact_sales(cleaned_data_dict["sales"], dim_product)
    fact_inventory = build_fact_inventory(cleaned_data_dict["inventory"], dim_product)
    fact_purchase_orders = build_fact_purchase_orders(cleaned_data_dict["purchase_orders"])
    fact_deliveries = build_fact_deliveries(cleaned_data_dict["deliveries"])
    
    tables = {
        "dim_date": dim_date,
        "dim_product": dim_product,
        "dim_supplier": dim_supplier,
        "dim_warehouse": dim_warehouse,
        "fact_sales": fact_sales,
        "fact_inventory": fact_inventory,
        "fact_purchase_orders": fact_purchase_orders,
        "fact_deliveries": fact_deliveries
    }
    
    # Export to CSV files in data/processed
    print("\n[Exporting Processed Star Schema CSVs]")
    for tname, df in tables.items():
        out_csv = os.path.join(PROCESSED_DATA_DIR, f"{tname}.csv")
        df.to_csv(out_csv, index=False)
        print(f" -> Saved {out_csv} ({len(df):,} rows)")
        
    # Write to SQLite DW
    print("\n[Loading into Relational Data Warehouse]")
    engine = get_db_engine()
    save_to_db(tables, engine)
    
    print("=" * 70)
    print("TRANSFORMATION AND DW LOADING COMPLETE!")
    print("=" * 70)
    return tables
