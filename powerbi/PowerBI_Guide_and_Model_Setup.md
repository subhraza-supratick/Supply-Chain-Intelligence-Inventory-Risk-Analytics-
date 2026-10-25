# Power BI Dashboard Build & Data Model Setup Guide

## 1. Overview & Data Source Ingestion

This guide outlines how to assemble the **Supply Chain Intelligence & Inventory Risk Analytics** 4-page executive dashboard in **Power BI Desktop**.

### Data Ingestion Options:
1. **Option A (CSV Directory - Recommended for Portability)**:
   - In Power BI Desktop: `Get Data` -> `Folder` or `Text/CSV`
   - Point to `data/processed/`:
     - `dim_date.csv`
     - `dim_product.csv`
     - `dim_supplier.csv`
     - `dim_warehouse.csv`
     - `fact_sales.csv`
     - `fact_inventory.csv`
     - `fact_purchase_orders.csv`
     - `fact_deliveries.csv`
     - `analytics_inventory_risk.csv`
     - `analytics_supplier_scorecard.csv`
     - `analytics_demand_forecasts.csv`
     - `demand_forecast_evaluation.csv`
2. **Option B (SQLite / PostgreSQL Database)**:
   - Use ODBC / PostgreSQL connector pointing to your active instance or `data/processed/supply_chain.db`.

---

## 2. Power BI Star Schema Data Relationships

In the **Model View**, configure the following active relationships:

| From (Fact Table) | Foreign Key | To (Dimension Table) | Primary Key | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fact_sales` | `product_id` | `dim_product` | `product_id` | `*:1` (Many-to-One) | Single |
| `fact_sales` | `warehouse_id` | `dim_warehouse` | `warehouse_id` | `*:1` (Many-to-One) | Single |
| `fact_sales` | `sale_date` | `dim_date` | `date` | `*:1` (Many-to-One) | Single |
| `fact_inventory` | `product_id` | `dim_product` | `product_id` | `*:1` (Many-to-One) | Single |
| `fact_inventory` | `warehouse_id` | `dim_warehouse` | `warehouse_id` | `*:1` (Many-to-One) | Single |
| `fact_inventory` | `inventory_date` | `dim_date` | `date` | `*:1` (Many-to-One) | Single |
| `fact_purchase_orders`| `supplier_id` | `dim_supplier` | `supplier_id` | `*:1` (Many-to-One) | Single |
| `fact_purchase_orders`| `product_id` | `dim_product` | `product_id` | `*:1` (Many-to-One) | Single |
| `fact_purchase_orders`| `warehouse_id` | `dim_warehouse` | `warehouse_id` | `*:1` (Many-to-One) | Single |
| `fact_deliveries` | `supplier_id` | `dim_supplier` | `supplier_id` | `*:1` (Many-to-One) | Single |
| `fact_deliveries` | `product_id` | `dim_product` | `product_id` | `*:1` (Many-to-One) | Single |
| `fact_deliveries` | `warehouse_id` | `dim_warehouse` | `warehouse_id` | `*:1` (Many-to-One) | Single |
| `analytics_inventory_risk` | `product_id` | `dim_product` | `product_id` | `*:1` (Many-to-One) | Single |
| `analytics_inventory_risk` | `warehouse_id` | `dim_warehouse` | `warehouse_id` | `*:1` (Many-to-One) | Single |

---

## 3. Design System & Visual Theme

- **Background Canvas**: Slate / Deep Navy (`#0F172A`)
- **Card & Container Background**: Charcoal Glassmorphism (`#1E293B`, Opacity 95%)
- **Primary Accent / Revenue**: Emerald Green (`#10B981`)
- **Warning / Medium Risk**: Amber Gold (`#F59E0B`)
- **Critical Risk / Stockout**: Crimson Coral (`#EF4444`)
- **Secondary Accent / Forecasting**: Cyan / Electric Indigo (`#38BDF8` / `#6366F1`)
- **Typography**: Inter / Segoe UI (Font size hierarchy: KPI Value 28pt Bold, Header 13pt Semi-bold, Body 10pt Regular).

---

## 4. Dashboard Page Layouts

### Page 1 — Executive Supply Chain Overview
**Objective**: High-level c-suite summary of financial revenue, inventory velocity, and SLA adherence.
* **Top KPI Cards**:
  - Total Revenue (`[Total Revenue]`)
  - Gross Profit Margin % (`[Gross Profit Margin %]`)
  - Inventory Turnover (`[Inventory Turnover Ratio]`)
  - Days Inventory Outstanding (`[Days Inventory Outstanding (DIO)]`)
  - Overall Stockout Rate % (`[Overall Stockout Rate %]`)
  - On-Time Delivery Rate % (`[Overall On Time Delivery %]`)
* **Visuals**:
  1. **Line & Clustered Column Chart**: Monthly Revenue & COGS Trend with MoM Growth Line.
  2. **Donut Chart**: Inventory Health Distribution (Healthy vs Low Stock vs Overstocked vs Stock-out).
  3. **Bar Chart**: Top 10 Best-Selling SKUs by Revenue.
  4. **Stacked Bar Chart**: Warehouse Fulfillment Volume & Value Contribution.
* **Slicers**: Date Range (Year/Quarter), Product Category, Warehouse Location.

---

### Page 2 — Inventory Risk & Optimization (Flagship Analytical View)
**Objective**: Immediate operational triage for stockout vulnerabilities, excess stock holding, and procurement action items.
* **Top KPI Cards**:
  - Critical Risk SKUs (`[Critical Risk SKU Count]`)
  - High Risk SKUs (`[High Risk SKU Count]`)
  - Current Stock-out SKUs (`[Stockout SKUs Currently]`)
  - Total Excess Inventory Value (`[Total Excess Inventory Value]`)
* **Core Visuals**:
  1. **Scatter Plot (Analytical Core)**:
     - **X-Axis**: Current Closing Stock (Units)
     - **Y-Axis**: Forecast Demand During Lead Time (Units)
     - **Bubble Size**: Current Inventory Value ($)
     - **Color Legend**: `risk_category` (Critical, High, Medium, Low)
     - *Insight*: Points high on Y and low on X represent immediate stock-out risks; points far right on X with low Y represent capital-draining excess inventory.
  2. **Triage Matrix / Interactive Table**:
     - Columns: `product_id`, `product_name`, `category`, `warehouse_name`, `current_closing_stock`, `forecast_demand_lead_time`, `days_of_inventory`, `inventory_risk_score`, `risk_category`, `recommended_action`
     - Conditional Formatting: Background color scale on `inventory_risk_score` (Red for >=80, Orange for 60-79, Green for <30).
* **Slicers**: `risk_category`, `abc_class`, `recommended_action`, `warehouse_name`.

---

### Page 3 — Demand Forecasting & Machine Learning
**Objective**: Comparison of historical sales patterns, machine learning demand forecasts, and future replenishment planning.
* **Top KPI Cards**:
  - Mean Absolute Error (`[Forecast MAE]`)
  - Forecast 30-Day Demand (`[Forecast 30-Day Demand]`)
  - Forecast Variance (`[Forecast Variance]`)
* **Visuals**:
  1. **Time-Series Multi-Line Chart**:
     - **X-Axis**: Date (`dim_date[date]`)
     - **Values**: Actual Quantity Sold vs Predicted Machine Learning Demand.
  2. **Feature Importance Horizontal Bar Chart**:
     - Feature weights from Random Forest model (`rolling_mean_28`, `day_of_year`, `rolling_mean_14`, `rolling_std_7`, `lag_7`).
  3. **SKU-Level Demand Projection Matrix**:
     - Forecast Daily Demand, Lead Time Demand Buffer, Next 30-Day Projections.
* **Slicers**: Product Selector, Category, Warehouse, Date Slider.

---

### Page 4 — Supplier SLA & Vendor Performance Scorecard
**Objective**: Comprehensive vendor ranking and procurement risk exposure analysis.
* **Top KPI Cards**:
  - Average On-Time Delivery % (`[Supplier On Time %]`)
  - Average Order Fill Rate % (`[Supplier Fill Rate %]`)
  - Average Transit Delay (`[Average Supplier Delay Days]`)
  - Overall Defect Rate % (`[Supplier Defect Rate %]`)
* **Visuals**:
  1. **Supplier Performance Ranking Table**:
     - Columns: `supplier_name`, `supplier_region`, `supplier_type`, `total_pos_issued`, `on_time_delivery_rate_pct`, `avg_delay_days`, `fill_rate_pct`, `defect_rate_pct`, `supplier_risk_score`, `supplier_rating`.
  2. **Scatter / Quadrant Chart**:
     - **X-Axis**: On-Time Delivery %
     - **Y-Axis**: Order Fill Rate %
     - **Size**: Procurement Spend ($)
  3. **Bar Chart**: Average Delay Days by Supplier Region & Vendor.
* **Slicers**: Supplier Region, Supplier Type, Rating Tier.

---

## 5. Verification Checklist

- [x] All 8 Star Schema tables loaded into Power BI Data Model
- [x] 1-to-many single direction relationships verified
- [x] All DAX formulas imported from `powerbi/DAX_Measures.dax`
- [x] Theme colors applied to charts and cards
- [x] Conditional formatting verified on Risk Score and Supplier SLA columns
