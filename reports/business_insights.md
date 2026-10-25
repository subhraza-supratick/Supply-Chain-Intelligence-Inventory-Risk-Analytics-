# Executive Business Insights & Supply Chain Risk Advisory (India - INR)

**Document Version:** 2.0.0 (India & INR Localized)  
**Target Audience:** Chief Operating Officer (COO), VP of Supply Chain, Head of Procurement  
**Analysis Period:** 18 Months (2024-01-01 to 2025-06-30)  
**Scope:** 500 SKUs across 5 Indian Regional Distribution Centers, 20 Strategic Indian Suppliers  
**Currency:** Indian Rupee (₹ / INR Crores)

---

## 1. Executive Summary

An end-to-end supply chain diagnostic was executed across company sales, inventory positions, procurement orders, and vendor delivery logs across Indian distribution hubs. The analytics pipeline identified critical inventory imbalances, supplier bottlenecks, and replenishment vulnerabilities:

- **Revenue & Demand Volume:** Generated **₹2,042.84 Crores in gross revenue** across **146,283 transactions**, delivering an overall gross profit margin of **21.84%** (Gross Profit: **₹446.12 Cr**).
- **Inventory Capital Trapped:** Current inventory holding stands at **₹771.24 Crores**. An estimated **₹146.80 Crores is tied up in slow-moving/excess inventory** (>120 days of supply), primarily in C-category accessories and home appliance lines.
- **Stock-Out Vulnerability Hotspots:** 6 high-velocity SKUs currently operate with critical stock-out exposure (forecast demand during lead time exceeds available inventory buffers in Bengaluru and Delhi NCR).
- **Supplier SLA Bifurcation:** While preferred tier vendors achieved **97.8% On-Time Delivery (OTD)**, two critical suppliers (**S004 - Delta Sourcing India** and **S011 - Krystal Microtech Hyderabad**) averaged **4.9 to 6.8 days of delay** and defect rates exceeding **3.8%**, disrupting upstream replenishment.

```
+---------------------------------------------------------------------------------------------------+
|                           INDIAN SUPPLY CHAIN HEALTH SNAPSHOT (INR)                               |
+--------------------------+--------------------------+----------------------+----------------------+
| Gross Revenue:           | Gross Margin:            | Inventory Turnover:  | Avg Supplier OTD:    |
| ₹2,042.84 Cr             | 21.84%                   | 4.15x / year         | 89.40%               |
+--------------------------+--------------------------+----------------------+----------------------+
| Working Capital Locked:  | Excess Inventory Value:  | Critical/High Risk:  | Total SKUs Analyzed: |
| ₹771.24 Cr               | ₹146.80 Cr (19.0%)       | 26 SKU-DCs           | 500 (2,500 pairs)    |
+--------------------------+--------------------------+----------------------+----------------------+
```

---

## 2. Key Findings & Diagnostic Insights

### Finding 1: Working Capital Asymmetry via Pareto ABC Analysis
- **Class A SKUs (28.0% of portfolio):** Drive **79.95% of total consumption value (₹1,279.06 Cr)**. These high-velocity items require stringent daily replenishment cycles and tighter safety stock margins.
- **Class C SKUs (44.6% of portfolio):** Represent only **5.01% of total consumption value (₹80.15 Cr)** but account for **54.2% of warehouse floor space** and over **₹96.5 Cr in dead/slow-moving inventory**.

```
[PARETO ABC DISTRIBUTION - INDIA]
Class A:  ████████████████████████████████████████  79.95% Value (140 SKUs)
Class B:  ███████▌                                  15.04% Value (137 SKUs)
Class C:  ██▌                                        5.01% Value (223 SKUs)
```

---

### Finding 2: Stock-Out Risks Concentrated in High-Velocity Electronics
- Demand during supplier lead time for fast-moving items in **Delhi NCR Northern Logistics Park (W003)** and **Bengaluru Fulfillment Hub (W001)** frequently breaches safety stock thresholds during festival peaks (Diwali, Dussehra, Year-End surge).
- 6 SKUs exhibit an **Inventory Risk Score > 80.0 (Critical)**, where current available inventory will be exhausted within 4 to 8 days, while vendor lead times average 14–21 days.

---

### Finding 3: Vendor Delivery Inconsistency as Primary Lead Time Inflator
- **Top Performing Vendors:** S001 (*Bharat Micro Electronics*), S003 (*Godrej Hardware*), and S015 (*Omega Global Materials Kolkata*) achieved **96.5% - 98.4% OTD** and fill rates above **98.0%**.
- **Underperforming Vendors:**
  - **S004 (Delta Sourcing Logistics India - South):** OTD = **78.2%**, Avg Delay = **4.91 days**, Defect Rate = **4.75%**.
  - **S011 (Krystal Microtech Hyderabad):** OTD = **80.1%**, Avg Delay = **6.82 days**, Defect Rate = **5.41%**.
  - *Impact:* Products mapped to S004 and S011 had a **3.4x higher probability of entering stock-out state** compared to products serviced by Tier 1 suppliers.

---

### Finding 4: Regional Distribution Center Discrepancies
- **Bengaluru Mega Fulfillment Center (W001):** Highest revenue generator (₹640.2 Cr, 31.3% share), highest inventory turnover (5.8x).
- **Hyderabad Distribution Hub (W002):** Suffered highest localized stock-out rate (4.2%) due to delayed inter-warehouse transfers from Mumbai Bhiwandi logistics depot.
- **Mumbai Bhiwandi Logistics Depot (W004):** Functions effectively as the primary west-zone port buffer, holding ₹228.5 Cr in inventory value with low DIO (52 days).

---

## 3. Machine Learning Demand Forecasting Impact

- **Predictive Performance:** The Random Forest Regressor demonstrated strong baseline forecasting performance on held-out test data:
  - **MAE:** 3.42 units/day
  - **RMSE:** 7.73 units/day
- **Key Feature Drivers:** 28-day rolling demand mean (18.05%), day of year seasonality (16.76%), 14-day rolling mean (13.62%), and 7-day rolling standard deviation (13.32%).
- **Operational Benefit:** Incorporating ML forecast demand during lead time directly into the **Risk Scoring Formula** allows procurement teams to preemptively place purchase orders 14 days before safety stock depletion.

---

## 4. Prioritized Action Plan & Strategic Recommendations

```
+----------+----------------------------------------------+----------------------------------+-----------------------+
| Priority | Recommended Action                           | Target Cohort / Location         | Financial Impact (INR)|
+----------+----------------------------------------------+----------------------------------+-----------------------+
| P1 (NOW) | Issue Expedited POs & Emergency Rebalancing  | 6 Critical Risk SKUs (W001, W003)| Prevents ~₹14.5 Cr in |
|          | Inter-warehouse transfer from W004 to W002.  |                                  | lost revenue / stockout|
+----------+----------------------------------------------+----------------------------------+-----------------------+
| P2 (30D) | Supplier SLA Renegotiation / Dual-Sourcing   | Vendors S004 & S011              | Reduces lead time by  |
|          | Enforce contractual penalty clauses for delay|                                  | 4.5 days avg.         |
+----------+----------------------------------------------+----------------------------------+-----------------------+
| P3 (60D) | Inventory Rationalization & Festive Markdown | 223 Class-C SKUs (>120 DOI)      | Releases ₹68.0 Cr in  |
|          | Bundle slow-moving items with Class-A sales. |                                  | trapped working cap.  |
+----------+----------------------------------------------+----------------------------------+-----------------------+
| P4 (90D) | Dynamic Safety Stock Automation in ERP       | Entire Portfolio (500 SKUs)      | Reduces holding costs |
|          | Transition from static days to ML lead buffer|                                  | by 12-15% annually.   |
+----------+----------------------------------------------+----------------------------------+-----------------------+
```
