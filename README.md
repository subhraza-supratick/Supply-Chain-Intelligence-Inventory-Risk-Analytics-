# Supply Chain Intelligence & Inventory Risk Analytics (India - INR)

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20SQLite-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Power BI](https://img.shields.io/badge/BI-Power%20BI-F2C811.svg?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end enterprise data analytics and machine learning system that transforms raw, fragmented supply chain records across Indian distribution centers into actionable inventory intelligence, supplier scorecards, demand forecasts, and multi-factor risk diagnostics.

---

## 1. Project Overview & Business Scenario

Modern multi-echelon supply chain networks in India face complex operational challenges:
- **Frequent Stock-Outs:** Revenue loss on high-velocity items due to delayed supplier replenishment and festival demand surges (Diwali, Dussehra).
- **Capital Trapped in Excess Inventory:** Working capital tied up in slow-moving inventory (>120 days of supply).
- **Supplier Volatility:** Unpredictable vendor lead times, low on-time delivery rates, and high defect percentages.
- **Lack of Decision Prioritization:** Procurement teams lack an automated, risk-ranked triage engine to identify which SKU-warehouse pairs need immediate attention.

### Business Objective
Build an automated, production-grade analytics pipeline that answers:
1. **Which products are at critical risk of stock-out across specific Indian distribution centers?**
2. **Which SKUs are overstocked, tying up working capital?**
3. **Which suppliers are chronically underperforming SLA thresholds?**
4. **What future demand should the company expect over upcoming lead times?**

---

## 2. End-to-End Architecture

```
                 RAW BUSINESS DATA (INR / ₹)
     (Sales, Inventory, Suppliers, POs, Deliveries)
                         |
                         v
             +-----------------------+
             |  PYTHON ETL PIPELINE  |
             |-----------------------|
             | Extract & Load        |
             | Clean & Standardize   |
             | Automated DQ Audit    |
             | Feature Engineering   |
             +-----------+-----------+
                         |
                         v
             +-----------------------+
             | POSTGRESQL / SQL DW   |
             |     (Star Schema)     |
             +-----------+-----------+
                         |
            +------------+------------+
            |                         |
            v                         v
   +------------------+      +------------------+
   |  SQL ANALYTICS   |      |    PYTHON ML     |
   |------------------|      |------------------|
   | Inventory KPIs   |      | Demand Forecast  |
   | Turnover & DIO   |      | (Random Forest)  |
   | Supplier Metrics |      | Multi-Factor     |
   | ABC Pareto Class |      | Risk Scoring     |
   +--------+---------+      +--------+---------+
            |                         |
            +------------+------------+
                         |
                         v
             +-----------------------+
             |   ANALYTICS TABLES    |
             +-----------+-----------+
                         |
                         v
             +-----------------------+
             |  POWER BI DASHBOARD   |
             |-----------------------|
             | 1. Executive Overview |
             | 2. Inventory Risk     |
             | 3. Demand Forecast    |
             | 4. Supplier Scorecard |
             +-----------+-----------+
                         |
                         v
             +-----------------------+
             |  BUSINESS INSIGHTS &  |
             |    RECOMMENDATIONS    |
             +-----------------------+
```

---

## 3. Technology Stack & Dataset Scope

| Domain | Technologies Used |
| :--- | :--- |
| **Data Scope** | Synthetic Indian Business Data (500 Products in INR ₹, 20 Indian Suppliers, 5 Regional DCs, 146K+ Sales Records) |
| **Database & Modeling** | PostgreSQL / SQLite, Relational Star Schema DDL, Constraints, Indexes |
| **Data Engineering (ETL)**| Python 3.10, Pandas, NumPy, SQLAlchemy, openpyxl |
| **Data Quality Layer** | Custom Automated Validation Suite (Nulls, Duplicates, Referential Integrity, Conservation Laws) |
| **Machine Learning** | Scikit-Learn (Random Forest Regressor, Time-Series Lag & Rolling Feature Engineering) |
| **Business Intelligence** | Power BI Desktop, Advanced DAX Measures, Star Schema Data Modeling |
| **Version Control & Dev** | Git, GitHub, VS Code, Jupyter Notebooks |

---

## 4. Star Schema Data Warehouse Design

- **Dimensions:**
  - [`dim_product`](file:///d:/PROJECTS/DA/DA2/data/processed/dim_product.csv): Product details, category, unit cost in ₹, selling price, lead times, safety stocks.
  - [`dim_supplier`](file:///d:/PROJECTS/DA/DA2/data/processed/dim_supplier.csv): Supplier registry across Indian manufacturing hubs (Bengaluru, Pune, Chennai, Noida, etc.).
  - [`dim_warehouse`](file:///d:/PROJECTS/DA/DA2/data/processed/dim_warehouse.csv): Regional Indian DCs (Bengaluru, Hyderabad, Delhi NCR, Mumbai Bhiwandi, Chennai).
  - [`dim_date`](file:///d:/PROJECTS/DA/DA2/data/processed/dim_date.csv): Comprehensive calendar dimension with year, quarter, month, ISO week, weekend flags.
- **Facts:**
  - [`fact_sales`](file:///d:/PROJECTS/DA/DA2/data/processed/fact_sales.csv): Granular transaction records with revenue in ₹, COGS, gross margins, and channels.
  - [`fact_inventory`](file:///d:/PROJECTS/DA/DA2/data/processed/fact_inventory.csv): Daily/periodic inventory balance tracking satisfying the conservation law.
  - [`fact_purchase_orders`](file:///d:/PROJECTS/DA/DA2/data/processed/fact_purchase_orders.csv): Procurement PO records, target vs actual lead times.
  - [`fact_deliveries`](file:///d:/PROJECTS/DA/DA2/data/processed/fact_deliveries.csv): Vendor shipment receipts, fill rates, transit times, damage rates.

---

## 5. Machine Learning Demand Forecasting

- **Feature Engineering:**
  - Time-series lags: `lag_1`, `lag_7`, `lag_14`, `lag_28`
  - Rolling statistics: `rolling_mean_7`, `rolling_mean_14`, `rolling_mean_28`, `rolling_std_7`
  - Calendar attributes: `day_of_week`, `month`, `quarter`, `day_of_year`, `is_weekend`
- **Chronological Split:**
  - **Training Window:** 2024-01-01 to 2025-03-31 (15 Months / 128.4K rows)
  - **Test Holdout:** 2025-04-01 to 2025-06-30 (3 Months / 27.3K rows)
- **Model:** `RandomForestRegressor(n_estimators=100, max_depth=12)`
- **Evaluation Metrics:**
  - **MAE:** 3.42 units/day
  - **RMSE:** 7.73 units/day

---

## 6. Multi-Factor Inventory Risk Scoring Engine

$$\text{Inventory Risk Score} = 0.30 \cdot R_{\text{Stockout}} + 0.25 \cdot R_{\text{Volatility}} + 0.20 \cdot R_{\text{Supplier}} + 0.15 \cdot R_{\text{LeadTime}} + 0.10 \cdot R_{\text{Excess}}$$

```
+---------------+---------------------+---------------------------------------------------------------+
| Score Range   | Risk Tier           | Prescriptive Action Recommendation                            |
+---------------+---------------------+---------------------------------------------------------------+
| 81 – 100      | Critical Risk       | Expedite Purchase Order & Emergency Inter-Warehouse Transfer  |
| 60 – 80       | High Risk           | Review Reorder Quantity & Increase Safety Stock Buffer        |
| 31 – 59       | Medium Risk         | Monitor Inventory & Re-evaluate Supplier SLA                  |
| 0 – 30        | Low Risk / Healthy  | Normal Monitoring & Scheduled Replenishment                   |
| 0 – 30 (DOI>120)| Low / Excess      | Liquidate / Festive Markdown on Excess Stock                  |
+---------------+---------------------+---------------------------------------------------------------+
```

---

## 7. Power BI Dashboard Architecture (4 Pages)

1. **Page 1: Executive Supply Chain Overview**
   - KPI Cards: Total Revenue (₹2,042.8 Cr), Gross Margin (21.84%), Inventory Turnover (4.15x), Overall Stockout Rate (1.8%), Supplier OTD (89.40%).
2. **Page 2: Inventory Risk & Optimization (Flagship View)**
   - Interactive Triage Matrix ranked by `inventory_risk_score`.
   - Analytical Scatter Plot: $X = \text{Current Stock}$, $Y = \text{Forecast Demand during Lead Time}$, $\text{Bubble Size} = \text{Inventory Value in ₹}$.
3. **Page 3: Demand Forecasting & Seasonality**
   - Actual Demand vs Random Forest Predicted Demand over time.
   - Feature Importance horizontal bar chart.
4. **Page 4: Supplier Performance & Vendor Scorecard**
   - Supplier Scorecard Table: OTD %, Average Delay Days, Fill Rate %, Defect Rate %, Spend in ₹.

---

## 8. Quickstart & Execution

```powershell
# 1. Generate Localized Indian Raw Data (146K+ transactions in ₹)
python src/data_generation/generate_data.py

# 2. Run ETL, DQ Audits, Star Schema Loading, ML Forecasting & Risk Scoring
python src/run_pipeline.py

# 3. Export to Excel Workbook for 1-Click Power BI Ingestion
python scripts/export_to_excel.py

# 4. Run Interactive Live System Demo
python scripts/demo_full_run.py
```
