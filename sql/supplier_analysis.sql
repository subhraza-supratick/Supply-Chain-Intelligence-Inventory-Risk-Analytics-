-- ==============================================================================
-- SUPPLIER PERFORMANCE & PROCUREMENT SQL ANALYTICS
-- Focus: On-Time Delivery Rate (OTD), Delay Days, Fill Rate, Defect Rate & Scorecard Ranking
-- ==============================================================================

-- 1. Complete Supplier Scorecard & Performance Metrics
SELECT
    s.supplier_id,
    s.supplier_name,
    s.supplier_region,
    s.supplier_type,
    COUNT(d.delivery_id) AS total_shipments,
    SUM(d.is_on_time) AS on_time_shipments,
    -- On-Time Delivery Rate %
    ROUND((CAST(SUM(d.is_on_time) AS FLOAT) / COUNT(d.delivery_id)) * 100, 2) AS on_time_delivery_rate_pct,
    -- Average Delay (Days)
    ROUND(AVG(d.delay_days), 2) AS avg_delay_days,
    -- Fill Rate % = (Total Received / Total Ordered) * 100
    ROUND((CAST(SUM(d.quantity_received) AS FLOAT) / NULLIF(SUM(d.quantity_ordered), 0)) * 100, 2) AS fill_rate_pct,
    -- Defect Rate % = (Total Damaged / Total Received) * 100
    ROUND((CAST(SUM(d.damaged_quantity) AS FLOAT) / NULLIF(SUM(d.quantity_received), 0)) * 100, 2) AS defect_rate_pct,
    -- Total Procurement Spend
    ROUND(SUM(po.total_po_cost), 2) AS total_procurement_spend
FROM dim_supplier s
LEFT JOIN fact_deliveries d ON s.supplier_id = d.supplier_id
LEFT JOIN fact_purchase_orders po ON d.po_id = po.po_id
GROUP BY s.supplier_id, s.supplier_name, s.supplier_region, s.supplier_type
ORDER BY on_time_delivery_rate_pct ASC, avg_delay_days DESC;

-- 2. Underperforming Suppliers Identified for SLA Review (OTD < 85% or Avg Delay > 3.0 Days)
SELECT
    s.supplier_id,
    s.supplier_name,
    s.supplier_region,
    COUNT(d.delivery_id) AS total_shipments,
    ROUND((CAST(SUM(d.is_on_time) AS FLOAT) / COUNT(d.delivery_id)) * 100, 2) AS on_time_rate_pct,
    ROUND(AVG(d.delay_days), 2) AS avg_delay_days,
    ROUND((CAST(SUM(d.damaged_quantity) AS FLOAT) / NULLIF(SUM(d.quantity_received), 0)) * 100, 2) AS defect_rate_pct,
    'High Risk - Contract Renegotiation / Secondary Supplier Activation' AS procurement_action
FROM dim_supplier s
JOIN fact_deliveries d ON s.supplier_id = d.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.supplier_region
HAVING (CAST(SUM(d.is_on_time) AS FLOAT) / COUNT(d.delivery_id)) < 0.85 
    OR AVG(d.delay_days) > 3.0
ORDER BY avg_delay_days DESC;

-- 3. Top Tier Preferred Suppliers (OTD >= 95% and Defect Rate < 1.5%)
SELECT
    s.supplier_id,
    s.supplier_name,
    s.supplier_region,
    COUNT(d.delivery_id) AS total_shipments,
    ROUND((CAST(SUM(d.is_on_time) AS FLOAT) / COUNT(d.delivery_id)) * 100, 2) AS on_time_rate_pct,
    ROUND(AVG(d.delay_days), 2) AS avg_delay_days,
    ROUND((CAST(SUM(d.damaged_quantity) AS FLOAT) / NULLIF(SUM(d.quantity_received), 0)) * 100, 2) AS defect_rate_pct,
    'Preferred Supplier - Strategic Long-Term Partnership Tier' AS status
FROM dim_supplier s
JOIN fact_deliveries d ON s.supplier_id = d.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.supplier_region
HAVING (CAST(SUM(d.is_on_time) AS FLOAT) / COUNT(d.delivery_id)) >= 0.95
   AND (CAST(SUM(d.damaged_quantity) AS FLOAT) / NULLIF(SUM(d.quantity_received), 0)) < 0.015
ORDER BY on_time_rate_pct DESC;
