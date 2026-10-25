-- ==============================================================================
-- SALES PERFORMANCE & REVENUE SQL ANALYTICS
-- Focus: Executive KPIs, Revenue Trends, Channel Breakdown & Top Products
-- ==============================================================================

-- 1. Executive Summary: Total Revenue, Total COGS, Gross Profit & Overall Profit Margin
SELECT
    COUNT(DISTINCT sale_id) AS total_orders,
    SUM(quantity_sold) AS total_units_sold,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    ROUND(SUM(total_cogs), 2) AS total_cogs,
    ROUND(SUM(gross_profit), 2) AS total_gross_profit,
    ROUND((SUM(gross_profit) / SUM(total_revenue)) * 100, 2) AS overall_profit_margin_pct
FROM fact_sales;

-- 2. Monthly Revenue & Profit Trend with Month-over-Month Growth
WITH monthly_metrics AS (
    SELECT
        d.year,
        d.month,
        d.year_month,
        SUM(s.quantity_sold) AS monthly_units,
        ROUND(SUM(s.total_revenue), 2) AS monthly_revenue,
        ROUND(SUM(s.gross_profit), 2) AS monthly_gross_profit
    FROM fact_sales s
    JOIN dim_date d ON s.sale_date = d.date
    GROUP BY d.year, d.month, d.year_month
)
SELECT
    year_month,
    monthly_units,
    monthly_revenue,
    monthly_gross_profit,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY year, month)) 
        / LAG(monthly_revenue, 1) OVER (ORDER BY year, month) * 100, 
        2
    ) AS mom_revenue_growth_pct
FROM monthly_metrics
ORDER BY year, month;

-- 3. Top 10 Best-Selling Products by Total Revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    SUM(s.quantity_sold) AS total_units_sold,
    ROUND(SUM(s.total_revenue), 2) AS total_revenue_generated,
    ROUND(SUM(s.gross_profit), 2) AS total_profit,
    ROUND((SUM(s.gross_profit) / SUM(s.total_revenue)) * 100, 2) AS margin_pct
FROM fact_sales s
JOIN dim_product p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.subcategory
ORDER BY total_revenue_generated DESC
LIMIT 10;

-- 4. Sales Revenue by Category & Subcategory
SELECT
    p.category,
    p.subcategory,
    COUNT(DISTINCT s.product_id) AS sku_count,
    SUM(s.quantity_sold) AS units_sold,
    ROUND(SUM(s.total_revenue), 2) AS total_revenue,
    ROUND(SUM(s.gross_profit), 2) AS total_profit,
    ROUND((SUM(s.total_revenue) / (SELECT SUM(total_revenue) FROM fact_sales)) * 100, 2) AS revenue_contribution_pct
FROM fact_sales s
JOIN dim_product p ON s.product_id = p.product_id
GROUP BY p.category, p.subcategory
ORDER BY p.category, total_revenue DESC;

-- 5. Sales Channel & Customer Segment Matrix
SELECT
    s.sales_channel,
    s.customer_type,
    COUNT(s.sale_id) AS transaction_count,
    SUM(s.quantity_sold) AS total_units,
    ROUND(SUM(s.total_revenue), 2) AS total_revenue,
    ROUND(AVG(s.total_revenue), 2) AS avg_order_value
FROM fact_sales s
GROUP BY s.sales_channel, s.customer_type
ORDER BY s.sales_channel, total_revenue DESC;

-- 6. Warehouse Fulfillment Contribution
SELECT
    w.warehouse_id,
    w.warehouse_name,
    w.city,
    w.state,
    SUM(s.quantity_sold) AS units_fulfilled,
    ROUND(SUM(s.total_revenue), 2) AS revenue_fulfilled,
    ROUND((SUM(s.total_revenue) / (SELECT SUM(total_revenue) FROM fact_sales)) * 100, 2) AS fulfillment_share_pct
FROM fact_sales s
JOIN dim_warehouse w ON s.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name, w.city, w.state
ORDER BY revenue_fulfilled DESC;
