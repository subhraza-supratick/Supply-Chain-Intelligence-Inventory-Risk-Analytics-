-- ==============================================================================
-- SUPPLY CHAIN INTELLIGENCE & INVENTORY RISK ANALYTICS
-- Database Data Warehouse Schema (Star Schema DDL)
-- Compatible with PostgreSQL & SQLite
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- 1. DIMENSION TABLES
-- -----------------------------------------------------------------------------

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    quarter_name VARCHAR(10) NOT NULL,
    year_quarter VARCHAR(15) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    year_month VARCHAR(10) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0 = Monday, 6 = Sunday
    day_name VARCHAR(15) NOT NULL,
    is_weekend INTEGER NOT NULL,
    is_quarter_end INTEGER NOT NULL
);

-- Dimension: Product
CREATE TABLE IF NOT EXISTS dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    unit_cost NUMERIC(12, 2) NOT NULL CHECK (unit_cost > 0),
    selling_price NUMERIC(12, 2) NOT NULL CHECK (selling_price >= unit_cost),
    gross_margin_pct NUMERIC(6, 2),
    reorder_point INTEGER NOT NULL DEFAULT 0,
    lead_time_days INTEGER NOT NULL DEFAULT 7,
    safety_stock INTEGER NOT NULL DEFAULT 0
);

-- Dimension: Supplier
CREATE TABLE IF NOT EXISTS dim_supplier (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    supplier_region VARCHAR(100) NOT NULL,
    supplier_type VARCHAR(100) NOT NULL,
    contract_start_date DATE
);

-- Dimension: Warehouse
CREATE TABLE IF NOT EXISTS dim_warehouse (
    warehouse_id VARCHAR(50) PRIMARY KEY,
    warehouse_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    warehouse_capacity INTEGER NOT NULL CHECK (warehouse_capacity > 0)
);

-- -----------------------------------------------------------------------------
-- 2. FACT TABLES
-- -----------------------------------------------------------------------------

-- Fact: Sales
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id VARCHAR(50) PRIMARY KEY,
    sale_date DATE NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    warehouse_id VARCHAR(50) NOT NULL,
    quantity_sold INTEGER NOT NULL CHECK (quantity_sold > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price > 0),
    unit_cost NUMERIC(12, 2) NOT NULL,
    total_revenue NUMERIC(14, 2) NOT NULL,
    total_cogs NUMERIC(14, 2) NOT NULL,
    gross_profit NUMERIC(14, 2) NOT NULL,
    profit_margin_pct NUMERIC(6, 2),
    customer_type VARCHAR(50),
    sales_channel VARCHAR(50),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
);

-- Fact: Inventory Snapshots
CREATE TABLE IF NOT EXISTS fact_inventory (
    inventory_date DATE NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    warehouse_id VARCHAR(50) NOT NULL,
    opening_stock INTEGER NOT NULL DEFAULT 0,
    stock_received INTEGER NOT NULL DEFAULT 0,
    quantity_sold INTEGER NOT NULL DEFAULT 0,
    damaged_stock INTEGER NOT NULL DEFAULT 0,
    closing_stock INTEGER NOT NULL DEFAULT 0,
    unit_cost NUMERIC(12, 2) NOT NULL,
    closing_inventory_value NUMERIC(14, 2) NOT NULL,
    is_stockout INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (inventory_date, product_id, warehouse_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
);

-- Fact: Purchase Orders
CREATE TABLE IF NOT EXISTS fact_purchase_orders (
    po_id VARCHAR(50) PRIMARY KEY,
    po_date DATE NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    warehouse_id VARCHAR(50) NOT NULL,
    ordered_quantity INTEGER NOT NULL CHECK (ordered_quantity > 0),
    expected_delivery_date DATE NOT NULL,
    actual_delivery_date DATE NOT NULL,
    unit_cost NUMERIC(12, 2) NOT NULL,
    total_po_cost NUMERIC(14, 2) NOT NULL,
    target_lead_time_days INTEGER NOT NULL,
    actual_lead_time_days INTEGER NOT NULL,
    delay_days INTEGER NOT NULL DEFAULT 0,
    is_delayed INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (supplier_id) REFERENCES dim_supplier(supplier_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
);

-- Fact: Deliveries
CREATE TABLE IF NOT EXISTS fact_deliveries (
    delivery_id VARCHAR(50) PRIMARY KEY,
    po_id VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    warehouse_id VARCHAR(50) NOT NULL,
    dispatch_date DATE NOT NULL,
    expected_delivery_date DATE NOT NULL,
    actual_delivery_date DATE NOT NULL,
    quantity_ordered INTEGER NOT NULL,
    quantity_received INTEGER NOT NULL,
    damaged_quantity INTEGER NOT NULL DEFAULT 0,
    transit_days INTEGER NOT NULL,
    delay_days INTEGER NOT NULL DEFAULT 0,
    is_on_time INTEGER NOT NULL DEFAULT 1,
    fill_rate_pct NUMERIC(6, 2),
    defect_rate_pct NUMERIC(6, 2),
    FOREIGN KEY (po_id) REFERENCES fact_purchase_orders(po_id),
    FOREIGN KEY (supplier_id) REFERENCES dim_supplier(supplier_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
);

-- -----------------------------------------------------------------------------
-- 3. INDEXES FOR QUERY OPTIMIZATION
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_sales_date ON fact_sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_prod ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_wh ON fact_sales(warehouse_id);

CREATE INDEX IF NOT EXISTS idx_inv_date ON fact_inventory(inventory_date);
CREATE INDEX IF NOT EXISTS idx_inv_prod_wh ON fact_inventory(product_id, warehouse_id);

CREATE INDEX IF NOT EXISTS idx_po_supplier ON fact_purchase_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_po_date ON fact_purchase_orders(po_date);

CREATE INDEX IF NOT EXISTS idx_deliv_supplier ON fact_deliveries(supplier_id);
CREATE INDEX IF NOT EXISTS idx_deliv_actual_date ON fact_deliveries(actual_delivery_date);
