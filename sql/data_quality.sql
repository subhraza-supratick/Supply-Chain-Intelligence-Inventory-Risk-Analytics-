-- ==============================================================================
-- DATA QUALITY & AUDIT VALIDATION SUITE (SQL)
-- Runs automated integrity tests on Star Schema tables
-- ==============================================================================

-- 1. Check for Duplicate Primary Keys
-- Expected: 0 rows returned
SELECT 'fact_sales' AS table_name, sale_id AS duplicate_key, COUNT(*) AS occurrences
FROM fact_sales
GROUP BY sale_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'dim_product' AS table_name, product_id, COUNT(*)
FROM dim_product
GROUP BY product_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'dim_supplier' AS table_name, supplier_id, COUNT(*)
FROM dim_supplier
GROUP BY supplier_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_inventory' AS table_name, inventory_date || '-' || product_id || '-' || warehouse_id, COUNT(*)
FROM fact_inventory
GROUP BY inventory_date, product_id, warehouse_id
HAVING COUNT(*) > 1;

-- 2. Check for Null Values in Critical Foreign Keys & Measures
-- Expected: 0 rows returned
SELECT 
    'fact_sales null check' AS test_name,
    COUNT(*) AS failing_records
FROM fact_sales
WHERE sale_id IS NULL 
   OR sale_date IS NULL 
   OR product_id IS NULL 
   OR warehouse_id IS NULL 
   OR quantity_sold IS NULL 
   OR unit_price IS NULL;

-- 3. Check for Non-Positive Quantities or Negative Financials
-- Expected: 0 rows returned
SELECT 
    'Negative or Zero Sales Values' AS test_name,
    COUNT(*) AS invalid_records
FROM fact_sales
WHERE quantity_sold <= 0 
   OR unit_price <= 0 
   OR total_revenue <= 0;

-- 4. Date Chronology Integrity Checks (PO vs Actual Delivery)
-- Expected: 0 rows returned (actual_delivery_date must be >= po_date)
SELECT 
    po_id, 
    po_date, 
    actual_delivery_date, 
    'Actual Delivery Prior to PO Date' AS issue_description
FROM fact_purchase_orders
WHERE actual_delivery_date < po_date;

-- 5. Referential Integrity / Orphan Record Check
-- Expected: 0 rows returned
SELECT 
    'Orphan Product in Sales' AS check_type,
    s.product_id
FROM fact_sales s
LEFT JOIN dim_product p ON s.product_id = p.product_id
WHERE p.product_id IS NULL
UNION ALL
SELECT 
    'Orphan Warehouse in Sales' AS check_type,
    s.warehouse_id
FROM fact_sales s
LEFT JOIN dim_warehouse w ON s.warehouse_id = w.warehouse_id
WHERE w.warehouse_id IS NULL;

-- 6. Inventory Equation Conservation Law Audit
-- Formula: closing_stock = opening_stock + stock_received - quantity_sold - damaged_stock
-- Expected: 0 rows returned
SELECT 
    inventory_date,
    product_id,
    warehouse_id,
    opening_stock,
    stock_received,
    quantity_sold,
    damaged_stock,
    closing_stock,
    (opening_stock + stock_received - quantity_sold - damaged_stock) AS calculated_closing,
    'Conservation Equation Discrepancy' AS audit_note
FROM fact_inventory
WHERE closing_stock != (opening_stock + stock_received - quantity_sold - damaged_stock)
  AND (opening_stock + stock_received - quantity_sold - damaged_stock) >= 0;
