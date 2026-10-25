-- ==============================================================================
-- INVENTORY HEALTH, TURNOVER & STOCK-OUT SQL ANALYTICS
-- Focus: Inventory Turnover, Days Inventory Outstanding (DIO), Stock-outs, Excess Stock & ABC Pareto
-- ==============================================================================

-- 1. Category-Level Inventory Turnover & Days Inventory Outstanding (DIO)
WITH cogs_summary AS (
    SELECT
        p.category,
        SUM(s.total_cogs) AS total_cogs
    FROM fact_sales s
    JOIN dim_product p ON s.product_id = p.product_id
    GROUP BY p.category
),
inventory_summary AS (
    SELECT
        p.category,
        AVG(i.closing_inventory_value) AS avg_inventory_value,
        SUM(i.is_stockout) AS stockout_events,
        COUNT(i.closing_stock) AS total_snapshots
    FROM fact_inventory i
    JOIN dim_product p ON i.product_id = p.product_id
    GROUP BY p.category
)
SELECT
    c.category,
    ROUND(c.total_cogs, 2) AS total_cogs,
    ROUND(inv.avg_inventory_value, 2) AS avg_inventory_value,
    -- Inventory Turnover = (Annualized COGS) / Avg Inventory Value (Assuming 18 months / 546 days)
    ROUND((c.total_cogs * (365.0 / 546.0)) / inv.avg_inventory_value, 2) AS inventory_turnover_ratio,
    -- Days Inventory Outstanding (DIO) = (Avg Inventory / Annualized COGS) * 365
    ROUND((inv.avg_inventory_value / (c.total_cogs * (365.0 / 546.0))) * 365.0, 1) AS dio_days,
    ROUND((CAST(inv.stockout_events AS FLOAT) / inv.total_snapshots) * 100, 2) AS stockout_rate_pct
FROM cogs_summary c
JOIN inventory_summary inv ON c.category = inv.category
ORDER BY inventory_turnover_ratio DESC;

-- 2. Top 15 Products with Highest Stock-out Rate
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.lead_time_days,
    p.safety_stock,
    COUNT(i.inventory_date) AS total_inventory_days,
    SUM(i.is_stockout) AS stockout_days,
    ROUND((CAST(SUM(i.is_stockout) AS FLOAT) / COUNT(i.inventory_date)) * 100, 2) AS stockout_rate_pct
FROM fact_inventory i
JOIN dim_product p ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.lead_time_days, p.safety_stock
HAVING SUM(i.is_stockout) > 0
ORDER BY stockout_rate_pct DESC
LIMIT 15;

-- 3. Slow-Moving & Excess Inventory Analysis (> 120 Days of Inventory)
WITH product_daily_demand AS (
    SELECT
        product_id,
        warehouse_id,
        SUM(quantity_sold) / 546.0 AS avg_daily_demand
    FROM fact_sales
    GROUP BY product_id, warehouse_id
),
latest_inventory AS (
    SELECT
        i.product_id,
        i.warehouse_id,
        i.closing_stock,
        i.closing_inventory_value
    FROM fact_inventory i
    INNER JOIN (
        SELECT product_id, warehouse_id, MAX(inventory_date) AS max_date
        FROM fact_inventory
        GROUP BY product_id, warehouse_id
    ) latest ON i.product_id = latest.product_id 
            AND i.warehouse_id = latest.warehouse_id 
            AND i.inventory_date = latest.max_date
)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    w.warehouse_name,
    li.closing_stock AS current_stock_units,
    ROUND(li.closing_inventory_value, 2) AS current_stock_value,
    ROUND(pdd.avg_daily_demand, 2) AS avg_daily_demand,
    ROUND(li.closing_stock / NULLIF(pdd.avg_daily_demand, 0), 1) AS days_of_inventory,
    CASE 
        WHEN (li.closing_stock / NULLIF(pdd.avg_daily_demand, 0)) > 150 THEN 'Severe Excess / Slow Moving'
        WHEN (li.closing_stock / NULLIF(pdd.avg_daily_demand, 0)) > 90 THEN 'Moderate Excess'
        ELSE 'Normal Range'
    END AS excess_status
FROM latest_inventory li
JOIN product_daily_demand pdd ON li.product_id = pdd.product_id AND li.warehouse_id = pdd.warehouse_id
JOIN dim_product p ON li.product_id = p.product_id
JOIN dim_warehouse w ON li.warehouse_id = w.warehouse_id
WHERE (li.closing_stock / NULLIF(pdd.avg_daily_demand, 0)) > 90
ORDER BY days_of_inventory DESC
LIMIT 20;

-- 4. Pareto ABC Classification via SQL Window Functions
WITH product_cogs AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.unit_cost,
        SUM(s.quantity_sold) AS total_units_sold,
        SUM(s.total_cogs) AS total_consumption_value
    FROM fact_sales s
    JOIN dim_product p ON s.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category, p.unit_cost
),
cumulative_cogs AS (
    SELECT
        product_id,
        product_name,
        category,
        unit_cost,
        total_units_sold,
        total_consumption_value,
        SUM(total_consumption_value) OVER (ORDER BY total_consumption_value DESC) AS running_cogs,
        SUM(total_consumption_value) OVER () AS grand_total_cogs
    FROM product_cogs
)
SELECT
    product_id,
    product_name,
    category,
    total_units_sold,
    ROUND(total_consumption_value, 2) AS total_consumption_value,
    ROUND((running_cogs / grand_total_cogs) * 100, 2) AS cumulative_value_pct,
    CASE
        WHEN (running_cogs / grand_total_cogs) <= 0.80 THEN 'A'
        WHEN (running_cogs / grand_total_cogs) <= 0.95 THEN 'B'
        ELSE 'C'
    END AS abc_class
FROM cumulative_cogs
ORDER BY total_consumption_value DESC;
