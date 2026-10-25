"""
Validate Data Module.
Runs comprehensive data quality checks, schema validations, referential integrity assertions,
and mathematical conservation rules across supply chain tables.
"""

import pandas as pd
import numpy as np

class DataQualityValidator:
    def __init__(self, data_dict):
        self.data = data_dict
        self.validation_results = []
        self.has_critical_errors = False
        
    def log_result(self, test_name, table_name, status, details, failed_count=0):
        res = {
            "test_name": test_name,
            "table": table_name,
            "status": status,
            "failed_count": failed_count,
            "details": details
        }
        self.validation_results.append(res)
        status_symbol = "PASS" if status == "PASSED" else ("WARN" if status == "WARNING" else "FAIL")
        print(f"[{status_symbol:<4}] {table_name:<18} | {test_name:<30} | {details}")
        if status == "FAILED":
            self.has_critical_errors = True

    def check_nulls(self):
        """Checks for unexpected null values across all tables."""
        for name, df in self.data.items():
            null_counts = df.isnull().sum()
            total_nulls = null_counts.sum()
            if total_nulls == 0:
                self.log_result("Null Value Check", name, "PASSED", "Zero null values found", 0)
            else:
                cols_with_nulls = null_counts[null_counts > 0].to_dict()
                self.log_result("Null Value Check", name, "WARNING", f"Nulls found: {cols_with_nulls}", int(total_nulls))

    def check_duplicates(self):
        """Checks for duplicate primary keys / duplicate rows."""
        key_map = {
            "products": ["product_id"],
            "suppliers": ["supplier_id"],
            "warehouses": ["warehouse_id"],
            "sales": ["sale_id"],
            "purchase_orders": ["po_id"],
            "deliveries": ["delivery_id"],
            "inventory": ["inventory_date", "product_id", "warehouse_id"]
        }
        
        for name, keys in key_map.items():
            if name in self.data:
                df = self.data[name]
                dup_count = df.duplicated(subset=keys).sum()
                if dup_count == 0:
                    self.log_result("Primary Key Uniqueness", name, "PASSED", f"Unique on {keys}", 0)
                else:
                    self.log_result("Primary Key Uniqueness", name, "FAILED", f"Found {dup_count} duplicate keys on {keys}", int(dup_count))

    def check_numeric_validity(self):
        """Validates that prices, costs, and quantities are strictly non-negative and positive where required."""
        # Sales
        df_sales = self.data.get("sales")
        if df_sales is not None:
            neg_qty = (df_sales["quantity_sold"] <= 0).sum()
            neg_price = (df_sales["unit_price"] <= 0).sum()
            if neg_qty == 0 and neg_price == 0:
                self.log_result("Quantity & Price Positive", "sales", "PASSED", "All sales qty and prices > 0", 0)
            else:
                self.log_result("Quantity & Price Positive", "sales", "FAILED", f"Invalid qty ({neg_qty}) or price ({neg_price})", int(neg_qty + neg_price))
                
        # Products
        df_prod = self.data.get("products")
        if df_prod is not None:
            invalid_cost = (df_prod["unit_cost"] <= 0).sum()
            invalid_margin = (df_prod["selling_price"] < df_prod["unit_cost"]).sum()
            if invalid_cost == 0 and invalid_margin == 0:
                self.log_result("Cost & Margin Validity", "products", "PASSED", "All costs > 0 and price >= cost", 0)
            else:
                self.log_result("Cost & Margin Validity", "products", "FAILED", f"Invalid cost ({invalid_cost}) or margin ({invalid_margin})", int(invalid_cost + invalid_margin))

    def check_date_chronology(self):
        """Ensures temporal logic (delivery after PO, etc.)."""
        # Purchase Orders
        df_po = self.data.get("purchase_orders")
        if df_po is not None:
            # actual_delivery >= po_date
            anomalies = (pd.to_datetime(df_po["actual_delivery_date"]) < pd.to_datetime(df_po["po_date"])).sum()
            if anomalies == 0:
                self.log_result("Date Chronology Logic", "purchase_orders", "PASSED", "All delivery dates >= PO date", 0)
            else:
                self.log_result("Date Chronology Logic", "purchase_orders", "FAILED", f"{anomalies} records have delivery prior to PO date", int(anomalies))

        # Deliveries
        df_deliv = self.data.get("deliveries")
        if df_deliv is not None:
            dispatch_anomalies = (pd.to_datetime(df_deliv["actual_delivery_date"]) < pd.to_datetime(df_deliv["dispatch_date"])).sum()
            if dispatch_anomalies == 0:
                self.log_result("Dispatch vs Delivery Date", "deliveries", "PASSED", "All deliveries arrive on or after dispatch", 0)
            else:
                self.log_result("Dispatch vs Delivery Date", "deliveries", "FAILED", f"{dispatch_anomalies} records have delivery prior to dispatch", int(dispatch_anomalies))

    def check_referential_integrity(self):
        """Verifies that all foreign keys reference valid primary keys in master tables."""
        valid_pids = set(self.data["products"]["product_id"])
        valid_sids = set(self.data["suppliers"]["supplier_id"])
        valid_wids = set(self.data["warehouses"]["warehouse_id"])
        
        # Check Sales
        df_sales = self.data["sales"]
        orphan_sales_prod = (~df_sales["product_id"].isin(valid_pids)).sum()
        orphan_sales_wh = (~df_sales["warehouse_id"].isin(valid_wids)).sum()
        if orphan_sales_prod == 0 and orphan_sales_wh == 0:
            self.log_result("Referential Integrity", "sales", "PASSED", "All product_id and warehouse_id exist in master tables", 0)
        else:
            self.log_result("Referential Integrity", "sales", "FAILED", f"Orphan products: {orphan_sales_prod}, Orphan warehouses: {orphan_sales_wh}", int(orphan_sales_prod + orphan_sales_wh))
            
        # Check Purchase Orders
        df_po = self.data["purchase_orders"]
        orphan_po_prod = (~df_po["product_id"].isin(valid_pids)).sum()
        orphan_po_sup = (~df_po["supplier_id"].isin(valid_sids)).sum()
        orphan_po_wh = (~df_po["warehouse_id"].isin(valid_wids)).sum()
        if orphan_po_prod == 0 and orphan_po_sup == 0 and orphan_po_wh == 0:
            self.log_result("Referential Integrity", "purchase_orders", "PASSED", "All foreign keys (product, supplier, warehouse) resolve", 0)
        else:
            self.log_result("Referential Integrity", "purchase_orders", "FAILED", f"Unresolved foreign keys in PO table", int(orphan_po_prod + orphan_po_sup + orphan_po_wh))

    def check_inventory_conservation(self):
        """Validates the fundamental stock equation: closing = opening + received - sold - damaged."""
        df_inv = self.data.get("inventory")
        if df_inv is not None:
            expected_closing = df_inv["opening_stock"] + df_inv["stock_received"] - df_inv["quantity_sold"] - df_inv["damaged_stock"]
            # Allow max(0, expected_closing) check
            diff = (df_inv["closing_stock"] - np.maximum(0, expected_closing)).abs()
            violations = (diff > 0).sum()
            if violations == 0:
                self.log_result("Inventory Conservation Law", "inventory", "PASSED", "closing = opening + received - sold - damaged matches exactly (100%)", 0)
            else:
                self.log_result("Inventory Conservation Law", "inventory", "FAILED", f"Found {violations} equation balance discrepancies", int(violations))

    def run_all_validations(self):
        print("=" * 70)
        print("RUNNING AUTOMATED DATA QUALITY & INTEGRITY TEST SUITE")
        print("=" * 70)
        self.check_nulls()
        self.check_duplicates()
        self.check_numeric_validity()
        self.check_date_chronology()
        self.check_referential_integrity()
        self.check_inventory_conservation()
        print("=" * 70)
        df_summary = pd.DataFrame(self.validation_results)
        passed_count = (df_summary["status"] == "PASSED").sum()
        total_tests = len(df_summary)
        print(f"Data Quality Test Summary: {passed_count}/{total_tests} Tests Passed.")
        print("=" * 70)
        return df_summary

def validate_all_data(cleaned_data_dict):
    validator = DataQualityValidator(cleaned_data_dict)
    summary_df = validator.run_all_validations()
    return summary_df, not validator.has_critical_errors
