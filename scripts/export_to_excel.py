"""
Export processed Star Schema and Raw tables into unified, multi-sheet Excel (.xlsx) workbooks.
Enables 1-click 'Get Data -> Excel workbook' ingestion into Microsoft Power BI Desktop.
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def export_workbooks():
    print("=" * 80)
    print("GENERATING ENTERPRISE EXCEL (.XLSX) WORKBOOKS FOR POWER BI")
    print("=" * 80)
    
    # -------------------------------------------------------------------------
    # 1. Raw Multi-Sheet Excel Workbook
    # -------------------------------------------------------------------------
    raw_xlsx_path = os.path.join(RAW_DIR, "supply_chain_raw_data.xlsx")
    print(f"\n[1/2] Creating Raw Data Workbook: {raw_xlsx_path}...")
    
    raw_files = {
        "Products": "products.csv",
        "Suppliers": "suppliers.csv",
        "Warehouses": "warehouses.csv",
        "Sales": "sales.csv",
        "Inventory": "inventory.csv",
        "Purchase_Orders": "purchase_orders.csv",
        "Deliveries": "deliveries.csv"
    }
    
    with pd.ExcelWriter(raw_xlsx_path, engine="openpyxl") as writer:
        for sheet_name, fname in raw_files.items():
            fpath = os.path.join(RAW_DIR, fname)
            if os.path.exists(fpath):
                # Sample sales/inventory if excessively large or write full
                df = pd.read_csv(fpath)
                print(f" -> Adding sheet '{sheet_name}' ({len(df):,} rows)...")
                # Excel max row limit is 1,048,576
                if len(df) > 500000:
                    df = df.iloc[:500000]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
    print(f" -> Saved Raw Excel Workbook: {raw_xlsx_path}")
    
    # -------------------------------------------------------------------------
    # 2. Processed Power BI Ready Multi-Sheet Excel Workbook
    # -------------------------------------------------------------------------
    processed_xlsx_path = os.path.join(PROCESSED_DIR, "supply_chain_powerbi_data.xlsx")
    print(f"\n[2/2] Creating Power BI Star Schema Workbook: {processed_xlsx_path}...")
    
    processed_files = {
        "Dim_Product": "dim_product.csv",
        "Dim_Supplier": "dim_supplier.csv",
        "Dim_Warehouse": "dim_warehouse.csv",
        "Dim_Date": "dim_date.csv",
        "Fact_Sales": "fact_sales.csv",
        "Fact_Inventory": "fact_inventory.csv",
        "Fact_Purchase_Orders": "fact_purchase_orders.csv",
        "Fact_Deliveries": "fact_deliveries.csv",
        "Inventory_Risk_Scores": "inventory_risk_scores.csv",
        "Supplier_Scorecard": "supplier_scorecard.csv",
        "ABC_Analysis": "abc_inventory_analysis.csv",
        "Demand_Forecasts": "demand_forecasts.csv"
    }
    
    with pd.ExcelWriter(processed_xlsx_path, engine="openpyxl") as writer:
        for sheet_name, fname in processed_files.items():
            fpath = os.path.join(PROCESSED_DIR, fname)
            if os.path.exists(fpath):
                df = pd.read_csv(fpath)
                print(f" -> Adding sheet '{sheet_name}' ({len(df):,} rows)...")
                # Excel limit safety
                if len(df) > 500000:
                    df = df.iloc[:500000]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
    print(f" -> Saved Power BI Excel Workbook: {processed_xlsx_path}")
    print("\n" + "=" * 80)
    print("EXCEL WORKBOOKS GENERATION COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    export_workbooks()
