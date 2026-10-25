"""
Script to generate 5 professional Jupyter Notebooks using standard library json.
"""

import os
import json

NOTEBOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "notebooks")
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python", "version": "3.10"},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def md_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": [source]}

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [source]
    }

def create_nb_01():
    cells = [
        md_cell("# 01. Supply Chain Data Exploration & Schema Overview\n\n## Project Objective\nExplore historical sales, inventory, procurement, supplier, and warehouse datasets to understand distribution patterns, data structures, and seasonal dynamics across 500 SKUs and 5 regional distribution centers."),
        code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

DATA_DIR = os.path.join('..', 'data', 'raw')

# Load raw datasets
products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'))
suppliers = pd.read_csv(os.path.join(DATA_DIR, 'suppliers.csv'))
warehouses = pd.read_csv(os.path.join(DATA_DIR, 'warehouses.csv'))
sales = pd.read_csv(os.path.join(DATA_DIR, 'sales.csv'))
inventory = pd.read_csv(os.path.join(DATA_DIR, 'inventory.csv'))
po = pd.read_csv(os.path.join(DATA_DIR, 'purchase_orders.csv'))
deliveries = pd.read_csv(os.path.join(DATA_DIR, 'deliveries.csv'))

print(f"Products:        {products.shape}")
print(f"Suppliers:       {suppliers.shape}")
print(f"Warehouses:      {warehouses.shape}")
print(f"Sales:           {sales.shape}")
print(f"Inventory Logs:  {inventory.shape}")
print(f"Purchase Orders: {po.shape}")
print(f"Deliveries:      {deliveries.shape}")"""),
        md_cell("### Product Portfolio Breakdown by Category"),
        code_cell("""cat_summary = products.groupby('category').agg(
    sku_count=('product_id', 'count'),
    avg_unit_cost=('unit_cost', 'mean'),
    avg_selling_price=('selling_price', 'mean'),
    avg_lead_time=('lead_time_days', 'mean')
).reset_index()
cat_summary['avg_margin_pct'] = ((cat_summary['avg_selling_price'] - cat_summary['avg_unit_cost']) / cat_summary['avg_selling_price']) * 100
cat_summary"""),
        md_cell("### Monthly Sales Revenue Trend"),
        code_cell("""sales['sale_date'] = pd.to_datetime(sales['sale_date'])
sales['total_revenue'] = sales['quantity_sold'] * sales['unit_price']

monthly_sales = sales.set_index('sale_date').resample('ME')['total_revenue'].sum().reset_index()

plt.figure(figsize=(12, 5))
plt.plot(monthly_sales['sale_date'], monthly_sales['total_revenue'] / 1e6, marker='o', color='#2563EB', linewidth=2.5)
plt.title('Monthly Sales Revenue (in Millions $)', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Revenue ($M)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()""")
    ]
    nb = make_notebook(cells)
    with open(os.path.join(NOTEBOOKS_DIR, '01_data_exploration.ipynb'), 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)
    print(" -> Generated 01_data_exploration.ipynb")

def create_nb_02():
    cells = [
        md_cell("# 02. Automated Data Quality & Integrity Audit\n\n## Objectives\n1. Perform null check, duplicate check, and negative value verification.\n2. Assert referential integrity across all foreign keys.\n3. Validate temporal logic (`actual_delivery_date >= po_date`).\n4. Audit mathematical conservation of daily stock balances: `closing = opening + received - sold - damaged`."),
        code_cell("""import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath('..'))
from src.etl.load_data import load_raw_csvs
from src.etl.clean_data import clean_all_data
from src.etl.validate_data import validate_all_data

raw_data = load_raw_csvs()
cleaned_data = clean_all_data(raw_data)
summary_df, is_valid = validate_all_data(cleaned_data)

print(f"\\nAll Automated Quality Checks Passed: {is_valid}")
summary_df"""),
        md_cell("### Audit Inventory Conservation Equation Discrepancies"),
        code_cell("""df_inv = cleaned_data['inventory'].copy()
df_inv['calculated_closing'] = df_inv['opening_stock'] + df_inv['stock_received'] - df_inv['quantity_sold'] - df_inv['damaged_stock']
df_inv['discrepancy'] = df_inv['closing_stock'] - np.maximum(0, df_inv['calculated_closing'])

print(f"Total Discrepancy Count: {(df_inv['discrepancy'] != 0).sum()}")
print(f"Max Absolute Discrepancy: {df_inv['discrepancy'].abs().max()}")""")
    ]
    nb = make_notebook(cells)
    with open(os.path.join(NOTEBOOKS_DIR, '02_data_quality.ipynb'), 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)
    print(" -> Generated 02_data_quality.ipynb")

def create_nb_03():
    cells = [
        md_cell("# 03. Inventory KPIs, Turnover, Stock-out & Pareto ABC Analysis\n\n## Key Analytics\n- Inventory Turnover Ratio & Days Inventory Outstanding (DIO)\n- Stock-out Rate per Product and Regional DC\n- Excess and Slow-Moving Inventory Identification (> 120 Days of Supply)\n- Pareto ABC Inventory Classification (80/15/5 rule)"),
        code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.abspath('..'))
from src.etl.load_data import PROCESSED_DATA_DIR

fact_sales = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'fact_sales.csv'))
fact_inv = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'fact_inventory.csv'))
dim_prod = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'dim_product.csv'))
risk_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'inventory_risk_scores.csv'))
abc_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'abc_inventory_analysis.csv'))

print("Loaded processed analytics tables.")"""),
        md_cell("### Pareto ABC Cumulative Value Distribution Curve"),
        code_cell("""plt.figure(figsize=(10, 5))
plt.plot(range(len(abc_df)), abc_df['cum_cogs_pct'], color='#0D9488', linewidth=2.5, label='Cumulative COGS Value %')
plt.axhline(80, color='#EF4444', linestyle='--', label='80% Cutoff (Class A)')
plt.axhline(95, color='#F59E0B', linestyle='--', label='95% Cutoff (Class B)')
plt.title('Pareto ABC Inventory Classification Curve', fontsize=14, fontweight='bold')
plt.xlabel('Product Rank (by Value)', fontsize=12)
plt.ylabel('Cumulative Value %', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()"""),
        md_cell("### Inventory Health and Risk Categories Distribution"),
        code_cell("""health_counts = risk_df['inventory_health_status'].value_counts()
print("Inventory Health Breakdown:")
print(health_counts)

plt.figure(figsize=(8, 4))
health_counts.plot(kind='bar', color=['#10B981', '#F59E0B', '#EF4444', '#6366F1'])
plt.title('SKUs by Inventory Health Status', fontsize=13, fontweight='bold')
plt.ylabel('SKU-Warehouse Count')
plt.xticks(rotation=15)
plt.show()""")
    ]
    nb = make_notebook(cells)
    with open(os.path.join(NOTEBOOKS_DIR, '03_inventory_analysis.ipynb'), 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)
    print(" -> Generated 03_inventory_analysis.ipynb")

def create_nb_04():
    cells = [
        md_cell("# 04. Supplier SLA & Procurement Performance Analytics\n\n## Key Metrics\n- On-Time Delivery (OTD) Rate %\n- Average Delivery Delay (Days)\n- Order Quantity Fill Rate %\n- Defect / Damage Rate %\n- Composite Vendor Risk Index & Tier Rating"),
        code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

PROCESSED_DIR = os.path.join('..', 'data', 'processed')
scorecard = pd.read_csv(os.path.join(PROCESSED_DIR, 'supplier_scorecard.csv'))

print(f"Analyzed {len(scorecard)} Suppliers.")
scorecard[['supplier_name', 'supplier_region', 'on_time_delivery_rate_pct', 'avg_delay_days', 'fill_rate_pct', 'defect_rate_pct', 'supplier_risk_score', 'supplier_rating']].sort_values(by='supplier_risk_score', ascending=False)"""),
        md_cell("### Supplier SLA Quadrant: On-Time Delivery vs Fill Rate"),
        code_cell("""plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    scorecard['on_time_delivery_rate_pct'],
    scorecard['fill_rate_pct'],
    s=scorecard['total_procurement_spend'] / 50000,
    c=scorecard['supplier_risk_score'],
    cmap='RdYlGn_r',
    edgecolors='black',
    alpha=0.85
)
plt.colorbar(scatter, label='Supplier Risk Score (Red=High Risk)')
plt.title('Supplier Performance Quadrant (Size = Spend)', fontsize=14, fontweight='bold')
plt.xlabel('On-Time Delivery Rate (%)', fontsize=12)
plt.ylabel('Order Fill Rate (%)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)

# Annotate outliers
for _, r in scorecard.iterrows():
    if r['supplier_risk_score'] > 40 or r['on_time_delivery_rate_pct'] > 97:
        plt.annotate(r['supplier_name'], (r['on_time_delivery_rate_pct'] + 0.3, r['fill_rate_pct']), fontsize=8)
plt.show()""")
    ]
    nb = make_notebook(cells)
    with open(os.path.join(NOTEBOOKS_DIR, '04_supplier_analysis.ipynb'), 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)
    print(" -> Generated 04_supplier_analysis.ipynb")

def create_nb_05():
    cells = [
        md_cell("# 05. Machine Learning Demand Forecasting & Evaluation\n\n## Methodological Workflow\n1. Feature Engineering: Lags (1, 7, 14, 28), Rolling statistics (7, 14, 28), Calendar seasonality.\n2. Chronological Train/Test Split (Jan 2024–Mar 2025 Train, Apr–Jun 2025 Test Holdout).\n3. Random Forest Regression demand modeling.\n4. Interview-grade evaluation: MAE, RMSE, MAPE, R2 score.\n5. Integration into Multi-Factor Inventory Risk Engine."),
        code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.abspath('..'))
from src.forecasting.feature_engineering import build_demand_features, split_chronological
from src.forecasting.train_model import train_demand_model, get_feature_importance
from src.forecasting.evaluate_model import evaluate_forecasts

PROCESSED_DIR = os.path.join('..', 'data', 'processed')
fact_sales = pd.read_csv(os.path.join(PROCESSED_DIR, 'fact_sales.csv'))

df_features = build_demand_features(fact_sales)
X_train, y_train, X_test, y_test, train_df, test_df, feature_cols = split_chronological(df_features, split_date='2025-04-01')

model = train_demand_model(X_train, y_train)
y_pred = model.predict(X_test)
metrics = evaluate_forecasts(y_test, y_pred)"""),
        md_cell("### Feature Importance Weights"),
        code_cell("""feat_imp = get_feature_importance(model, feature_cols)

plt.figure(figsize=(10, 5))
plt.barh(feat_imp['feature'][::-1], feat_imp['importance_pct'][::-1], color='#6366F1')
plt.title('Demand Forecasting - Feature Importance (%)', fontsize=14, fontweight='bold')
plt.xlabel('Importance Percentage (%)')
plt.show()"""),
        md_cell("### Actual vs Forecast Demand Comparison (Test Sample)"),
        code_cell("""test_sample = test_df.copy()
test_sample['predicted_demand'] = y_pred

sample_series = test_sample[(test_sample['product_id'] == test_sample['product_id'].iloc[0]) & 
                            (test_sample['warehouse_id'] == 'W001')].sort_values('sale_date')

plt.figure(figsize=(12, 5))
plt.plot(pd.to_datetime(sample_series['sale_date']), sample_series['quantity_sold'], label='Actual Demand', color='#1E293B', linewidth=2)
plt.plot(pd.to_datetime(sample_series['sale_date']), sample_series['predicted_demand'], label='Random Forest Forecast', color='#38BDF8', linestyle='--', linewidth=2)
plt.title(f"Actual vs Predicted Daily Demand ({sample_series['product_id'].iloc[0]} @ W001)", fontsize=14, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Units Sold / Day')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()""")
    ]
    nb = make_notebook(cells)
    with open(os.path.join(NOTEBOOKS_DIR, '05_demand_forecasting.ipynb'), 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)
    print(" -> Generated 05_demand_forecasting.ipynb")

if __name__ == "__main__":
    create_nb_01()
    create_nb_02()
    create_nb_03()
    create_nb_04()
    create_nb_05()
    print("All 5 Jupyter Notebooks built successfully!")
