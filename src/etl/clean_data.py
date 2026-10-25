"""
Clean Data Module.
Performs data type conversions, trims whitespace, standardizes casing, handles nulls,
and removes exact duplicates from raw datasets.
"""

import pandas as pd
import numpy as np

def clean_products(df_products):
    """Clean and standardize products dataset."""
    df = df_products.copy()
    
    # Strip whitespace & standardize strings
    for col in ["product_id", "product_name", "category", "subcategory"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Ensure numeric columns
    numeric_cols = ["unit_cost", "selling_price", "reorder_point", "lead_time_days", "safety_stock"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    # Validation / defaults
    df["unit_cost"] = df["unit_cost"].clip(lower=0.01)
    df["selling_price"] = df["selling_price"].clip(lower=df["unit_cost"])
    df["reorder_point"] = df["reorder_point"].fillna(0).astype(int)
    df["lead_time_days"] = df["lead_time_days"].fillna(7).astype(int)
    df["safety_stock"] = df["safety_stock"].fillna(0).astype(int)
    
    df = df.drop_duplicates(subset=["product_id"])
    return df

def clean_suppliers(df_suppliers):
    """Clean and standardize suppliers dataset."""
    df = df_suppliers.copy()
    
    for col in ["supplier_id", "supplier_name", "supplier_region", "supplier_type"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    df["contract_start_date"] = pd.to_datetime(df["contract_start_date"], errors="coerce")
    df = df.drop_duplicates(subset=["supplier_id"])
    return df

def clean_warehouses(df_warehouses):
    """Clean and standardize warehouses dataset."""
    df = df_warehouses.copy()
    
    for col in ["warehouse_id", "warehouse_name", "city", "state"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    df["warehouse_capacity"] = pd.to_numeric(df["warehouse_capacity"], errors="coerce").fillna(0).astype(int)
    df = df.drop_duplicates(subset=["warehouse_id"])
    return df

def clean_sales(df_sales):
    """Clean and standardize sales transactions."""
    df = df_sales.copy()
    
    df["sale_id"] = df["sale_id"].astype(str).str.strip()
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["warehouse_id"] = df["warehouse_id"].astype(str).str.strip()
    
    df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce").fillna(0).astype(int)
    df["quantity_sold"] = df["quantity_sold"].clip(lower=0)
    
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    df["unit_price"] = df["unit_price"].clip(lower=0.01)
    
    df["customer_type"] = df["customer_type"].astype(str).str.strip()
    df["sales_channel"] = df["sales_channel"].astype(str).str.strip()
    
    # Drop records with invalid dates or zero quantity
    df = df.dropna(subset=["sale_date"])
    df = df[df["quantity_sold"] > 0]
    df = df.drop_duplicates(subset=["sale_id"])
    return df

def clean_inventory(df_inventory):
    """Clean and standardize inventory snapshot dataset."""
    df = df_inventory.copy()
    
    df["inventory_date"] = pd.to_datetime(df["inventory_date"], errors="coerce")
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["warehouse_id"] = df["warehouse_id"].astype(str).str.strip()
    
    int_cols = ["opening_stock", "stock_received", "quantity_sold", "damaged_stock", "closing_stock"]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        df[col] = df[col].clip(lower=0)
        
    df = df.dropna(subset=["inventory_date"])
    df = df.drop_duplicates(subset=["inventory_date", "product_id", "warehouse_id"])
    return df

def clean_purchase_orders(df_po):
    """Clean and standardize purchase orders dataset."""
    df = df_po.copy()
    
    df["po_id"] = df["po_id"].astype(str).str.strip()
    df["supplier_id"] = df["supplier_id"].astype(str).str.strip()
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["warehouse_id"] = df["warehouse_id"].astype(str).str.strip()
    
    df["po_date"] = pd.to_datetime(df["po_date"], errors="coerce")
    df["expected_delivery_date"] = pd.to_datetime(df["expected_delivery_date"], errors="coerce")
    df["actual_delivery_date"] = pd.to_datetime(df["actual_delivery_date"], errors="coerce")
    
    df["ordered_quantity"] = pd.to_numeric(df["ordered_quantity"], errors="coerce").fillna(0).astype(int).clip(lower=1)
    df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce").fillna(0.01).clip(lower=0.01)
    
    df = df.dropna(subset=["po_date"])
    df = df.drop_duplicates(subset=["po_id"])
    return df

def clean_deliveries(df_deliveries):
    """Clean and standardize deliveries dataset."""
    df = df_deliveries.copy()
    
    df["delivery_id"] = df["delivery_id"].astype(str).str.strip()
    df["po_id"] = df["po_id"].astype(str).str.strip()
    df["supplier_id"] = df["supplier_id"].astype(str).str.strip()
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["warehouse_id"] = df["warehouse_id"].astype(str).str.strip()
    
    df["dispatch_date"] = pd.to_datetime(df["dispatch_date"], errors="coerce")
    df["expected_delivery_date"] = pd.to_datetime(df["expected_delivery_date"], errors="coerce")
    df["actual_delivery_date"] = pd.to_datetime(df["actual_delivery_date"], errors="coerce")
    
    int_cols = ["quantity_ordered", "quantity_received", "damaged_quantity"]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int).clip(lower=0)
        
    df = df.dropna(subset=["actual_delivery_date"])
    df = df.drop_duplicates(subset=["delivery_id"])
    return df

def clean_all_data(raw_data_dict):
    """
    Executes cleaning functions on all raw datasets.
    """
    print("--- Starting Data Cleaning ---")
    cleaned = {
        "products": clean_products(raw_data_dict["products"]),
        "suppliers": clean_suppliers(raw_data_dict["suppliers"]),
        "warehouses": clean_warehouses(raw_data_dict["warehouses"]),
        "sales": clean_sales(raw_data_dict["sales"]),
        "inventory": clean_inventory(raw_data_dict["inventory"]),
        "purchase_orders": clean_purchase_orders(raw_data_dict["purchase_orders"]),
        "deliveries": clean_deliveries(raw_data_dict["deliveries"])
    }
    for name, df in cleaned.items():
        print(f" -> Cleaned {name}: {len(df):,} valid rows remaining")
    return cleaned
