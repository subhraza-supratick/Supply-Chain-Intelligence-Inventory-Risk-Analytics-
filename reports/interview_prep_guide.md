# Supply Chain Intelligence & Inventory Risk Analytics: Interview Defense & Mastery Guide (India & INR Localized)

This guide prepares you to present, explain, and defend every design decision, SQL query, ML model, and Power BI DAX measure in technical and behavioral interviews for Indian and global enterprise roles.

---

## 1. The 60-Second "Elevator Pitch" (Opening Response)

**Interviewer:** *"Walk me through your Supply Chain Intelligence project."*

> **Your Response:**  
> *"In this project, I built an end-to-end supply chain analytics and inventory intelligence system tailored to the Indian consumer electronics and durables market, solving two major enterprise challenges: **frequent stock-outs on fast-moving items** and **working capital trapped in slow-moving inventory** across 500 SKUs and 5 regional distribution centers (Bengaluru, Hyderabad, Delhi NCR, Mumbai Bhiwandi, and Chennai).  
> 
> Rather than just building a dashboard, I engineered the entire pipeline from the ground up:  
> 1. Ingested 18 months of sales (₹2,042 Cr revenue / 146K+ transactions), inventory, and procurement records into a **PostgreSQL Star Schema Data Warehouse** with an automated **21-point data quality test suite** that verified mathematical stock conservation.  
> 2. Implemented advanced **SQL analytics** for inventory turnover, DIO, Pareto ABC categorization, and supplier SLA scorecards across 20 Indian manufacturing partners.  
> 3. Developed a **Random Forest demand forecasting model** in Python using 28-day time-series lag and rolling features with strict chronological holdout evaluation (3.42 MAE), accounting for festival seasonality (Diwali/Dussehra surges).  
> 4. Synthesized these outputs into a **0–100 Multi-Factor Inventory Risk Scoring Engine** that flags stockout emergencies and prescribes automated actions (*Expedite PO*, *Increase Safety Stock*, *Markdown Excess*).  
> 5. Finally, I delivered an enterprise **4-page interactive Power BI dashboard** utilizing 25+ custom DAX measures for executive and operational triage."*

---

## 2. Technical Architecture & Design Decisions

### Q: Why did you model the data in a Star Schema instead of a 3NF normalized model or One Big Table (OBT)?
* **Answer:**  
  * *"In transactional systems (OLTP), 3NF is great for write performance and eliminating redundancy. However, for analytical querying (OLAP) and Power BI reporting, 3NF requires too many expensive multi-table joins that slow down DAX calculations.*
  * *On the other hand, a Single 'One Big Table' creates massive data duplication and makes time-intelligence and role-playing dimensions (like multiple dates for PO date vs actual delivery date) difficult to manage.*
  * *A **Star Schema** with 4 Dimensions (`dim_product`, `dim_supplier`, `dim_warehouse`, `dim_date`) and 4 Fact tables (`fact_sales`, `fact_inventory`, `fact_purchase_orders`, `fact_deliveries`) provides the optimal balance: fast filter propagation, intuitive 1-to-many single-direction relationships, and sub-second DAX query execution in Power BI's VertiPaq engine."*

---

### Q: How did you ensure Data Quality and prevent pipeline errors?
* **Answer:**  
  * *"I built an automated 21-point Data Quality layer in Python (`validate_data.py`) and SQL (`data_quality.sql`) that executes before any reporting tables are loaded. It tests:*
    1. * **Null & Duplicate Checks:** Primary key uniqueness across all tables.
    2. * **Referential Integrity:** Ensuring zero orphan foreign keys between sales/POs and master product/supplier tables.
    3. * **Temporal Chronology:** Verifying that `actual_delivery_date >= po_date` and `dispatch_date >= po_date`.
    4. * **Stock Conservation Equation:** Mathematically auditing the fundamental balance law:  
       $$\text{Closing Stock} = \text{Opening Stock} + \text{Received} - \text{Sold} - \text{Damaged}$$
       *All 21 automated validation tests passed with 100% data integrity."*

---

## 3. Machine Learning & Demand Forecasting Defense

### Q: Why did you choose Random Forest Regressor over ARIMA, Prophet, or Linear Regression?
* **Answer:**  
  * *"Traditional ARIMA and statistical smoothing models struggle when applied across hundreds of individual SKU-warehouse series with non-linear holiday interactions (like Indian Diwali/Navratri demand spikes).*
  * *Linear regression cannot naturally capture non-linear calendar spikes.*
  * ***Random Forest Regressor** excels here because:*
    1. *It easily handles tabular feature matrices combining **lags (`lag_1`, `lag_7`, `lag_14`, `lag_28`)**, **rolling window statistics (`rolling_mean_7`, `rolling_mean_14`, `rolling_mean_28`, `rolling_std_7`)**, and calendar seasonality.*
    2. *It is robust to outliers and does not assume normal distributions.*
    3. *It provides explicit **Feature Importances**, showing that the 28-day rolling average (18.05%) and day-of-year seasonality (16.76%) were the strongest predictors of future demand."*

---

## 4. Multi-Factor Inventory Risk Scoring Engine

### Q: How is the Inventory Risk Score calculated, and why 0–100?
* **Answer:**  
  * *"Traditional ERPs use binary min/max reorder flags, which fail to capture supplier delays or demand volatility. I engineered a composite **0–100 Multi-Factor Risk Index** with calibrated business weights:*
    $$\text{Risk Score} = 0.30 \cdot R_{\text{Stockout}} + 0.25 \cdot R_{\text{Volatility}} + 0.20 \cdot R_{\text{Supplier}} + 0.15 \cdot R_{\text{LeadTime}} + 0.10 \cdot R_{\text{Excess}}$$
  * **Component Breakdown:**
    * **30% Stockout Shortage:** Compares available stock against ML forecast demand during supplier lead time.
    * **25% Demand Volatility:** Coefficient of Variation ($CV = \sigma / \mu$) capturing unpredictability.
    * **20% Supplier Risk:** Vendor unreliability, historical delay frequency, and defect rate penalties.
    * **15% Lead Time Risk:** Exposure penalty for items with long replenishment cycles (e.g., 21–28 days).
    * **10% Excess Inventory:** Holding cost penalty for stock exceeding 120 days of supply.
  * **Actionable Mapping:**
    * **Score $\ge 80$ (Critical):** *Expedite PO & Inter-Warehouse Emergency Transfer*
    * **Score $60-79$ (High):** *Review Reorder Point & Increase Safety Stock Buffer*
    * **Score $30-59$ (Medium):** *Monitor Inventory & Re-evaluate Supplier SLA*
    * **Score $<30$ (Low):** *Normal Replenishment / Markdown Excess if DOI > 120*"*

---

## 5. Key Business Findings (In INR Crores)

1. **Working Capital Trapped:**  
   * *"The company holds **₹771.24 Crores in total inventory value**, of which **₹146.80 Crores (19.0%) is tied up in slow-moving/excess stock** (>120 days of supply), primarily in C-category accessories."*
2. **Pareto 80/20 Rule Confirmed:**  
   * *"Class A items represent only **28.0% of SKUs (140 products)** but generate **79.95% of total consumption value (₹1,279.06 Cr)**. Conversely, Class C items represent 44.6% of SKUs but only 5.01% of consumption value."*
3. **Supplier SLA Bottlenecks Identified:**  
   * *"Two vendors—**S004 (Delta Sourcing India - South)** and **S011 (Krystal Microtech Hyderabad)**—account for the majority of delivery disruptions with on-time delivery rates below **82%** and average delays of **4.9 to 6.8 days**, directly causing upstream stockouts in Delhi and Bengaluru."*
4. **Immediate Triage Executed:**  
   * *"Identified **6 Critical Risk SKUs** where current inventory will run out within 4–8 days before supplier replenishment arrives, prompting expedited purchase orders and stock rebalancing from Mumbai port."*

---

## 6. Resume Bullet Points (Ready to Copy-Paste)

```markdown
• Built an end-to-end Supply Chain Analytics & Inventory Intelligence pipeline across 500 SKUs (₹2,042 Cr revenue, 146K+ transactions), integrating sales, inventory, and procurement data into a PostgreSQL Star Schema with a 21-point automated data quality test suite.
• Implemented advanced SQL analytics and Pareto ABC classification to identify ₹146.8 Cr in trapped working capital across slow-moving inventory (>120 DOI) and quantify supplier SLA compliance (OTD %, fill rate, defect rate).
• Developed a Random Forest demand forecasting model in Python with 28-day lag/rolling features and chronological holdout evaluation (MAE: 3.42 units/day), feeding a 0–100 Multi-Factor Inventory Risk Scoring Engine with automated action recommendations.
• Designed an enterprise 4-page Power BI dashboard with 25+ DAX measures (Executive Overview, Inventory Risk Triage, ML Demand Forecast, and Supplier Scorecard) supporting real-time cross-filtering across 5 regional distribution centers.
```
