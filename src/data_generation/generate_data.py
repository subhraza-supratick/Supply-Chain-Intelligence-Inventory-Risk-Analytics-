"""
Streamlined, Interview-Optimized Data Generator (India & INR Localized).
Designed for crisp, memorable interview explanations:
- 60 Relatable SKUs (Electronics, Home Appliances, Office, Accessories)
- 8 Strategic Indian Suppliers (Bengaluru, Pune, Chennai, Noida, Hyderabad, etc.)
- 4 Key Distribution Hubs (Bengaluru W001, Delhi NCR W002, Mumbai W003, Chennai W004)
- 12 Months of Sales (~18,000 clean transactions, ~₹28.5 Crores revenue)
- Crystal-clear business storylines: 4 Critical Stockouts, ₹1.4 Cr Excess Inventory, 2 Problem Suppliers.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------------------
# 1. GENERATE 60 INTUITIVE & MEMORABLE PRODUCTS
# -------------------------------------------------------------------------
def generate_products():
    catalog = [
        # Electronics (15 SKUs)
        ("ELEC", "Pro Ultrabook Laptop 15", "Electronics", "Laptops", 52000, 68000, 14, "Fast"),
        ("ELEC", "Business Laptop Core i7", "Electronics", "Laptops", 44000, 58000, 14, "Fast"),
        ("ELEC", "Student Laptop Slim 14", "Electronics", "Laptops", 28000, 36000, 12, "Medium"),
        ("ELEC", "4K Ultra Gaming Monitor 27", "Electronics", "Monitors", 18500, 24999, 10, "Fast"),
        ("ELEC", "FHD Office Monitor 24", "Electronics", "Monitors", 9200, 12500, 7, "Medium"),
        ("ELEC", "Curved Designer Monitor 32", "Electronics", "Monitors", 26000, 34500, 14, "Slow"),
        ("ELEC", "Wireless ANC Headphones Pro", "Electronics", "Audio", 4500, 6999, 7, "Fast"),
        ("ELEC", "Bluetooth Soundbar 120W", "Electronics", "Audio", 6800, 9999, 10, "Medium"),
        ("ELEC", "True Wireless Earbuds Elite", "Electronics", "Audio", 2200, 3499, 5, "Fast"),
        ("ELEC", "Smart Fitness Watch Ultra", "Electronics", "Smart Devices", 3200, 4999, 7, "Fast"),
        ("ELEC", "Smart Home Security Camera", "Electronics", "Smart Devices", 2400, 3699, 7, "Medium"),
        ("ELEC", "Smart Wi-Fi Mesh Router", "Electronics", "Smart Devices", 3800, 5499, 10, "Slow"),
        ("ELEC", "Digital Inverter Backup 1100VA", "Electronics", "Power Solutions", 7500, 10500, 14, "Medium"),
        ("ELEC", "Heavy Duty UPS 1500VA", "Electronics", "Power Solutions", 11000, 15500, 15, "Slow"),
        ("ELEC", "Fast Charging Power Bank 20000mAh", "Electronics", "Power Solutions", 1400, 2199, 5, "Fast"),

        # Home Appliances (15 SKUs)
        ("HOME", "HEPA Smart Air Purifier Pro", "Home Appliances", "Air Purifiers", 8500, 12999, 14, "Fast"),
        ("HOME", "Compact Room Air Purifier", "Home Appliances", "Air Purifiers", 5200, 7999, 10, "Medium"),
        ("HOME", "Car Air Ionizer Purifier", "Home Appliances", "Air Purifiers", 1800, 2799, 7, "Slow"),
        ("HOME", "Espresso Coffee Maker 15-Bar", "Home Appliances", "Coffee Makers", 7200, 10999, 12, "Medium"),
        ("HOME", "Drip Filter Coffee Brewer", "Home Appliances", "Coffee Makers", 2400, 3699, 7, "Slow"),
        ("HOME", "Cold Brew Maker Stainless", "Home Appliances", "Coffee Makers", 1600, 2499, 7, "Slow"),
        ("HOME", "Heavy Duty Mixer Grinder 750W", "Home Appliances", "Mixer Grinders", 3200, 4799, 8, "Fast"),
        ("HOME", "Nutri-Bullet High Speed Blender", "Home Appliances", "Mixer Grinders", 2800, 4199, 7, "Medium"),
        ("HOME", "Commercial Juicer Grinder 1000W", "Home Appliances", "Mixer Grinders", 5500, 7999, 10, "Slow"),
        ("HOME", "Smart RGB Ambient Light Kit", "Home Appliances", "Smart Lighting", 1900, 2999, 7, "Fast"),
        ("HOME", "Smart LED Ceiling Panel 36W", "Home Appliances", "Smart Lighting", 1400, 2199, 6, "Medium"),
        ("HOME", "Motion Sensor Outdoor Lamp", "Home Appliances", "Smart Lighting", 950, 1499, 5, "Slow"),
        ("HOME", "Cordless Stick Vacuum Cleaner", "Home Appliances", "Vacuum Cleaners", 9500, 14499, 14, "Fast"),
        ("HOME", "Robot Vacuum Cleaner Auto-Mop", "Home Appliances", "Vacuum Cleaners", 18000, 26999, 18, "Medium"),
        ("HOME", "Handheld Car Vacuum 120W", "Home Appliances", "Vacuum Cleaners", 1600, 2499, 7, "Slow"),

        # Accessories (15 SKUs)
        ("ACCE", "Mechanical RGB Gaming Keyboard", "Accessories", "Keyboards", 2200, 3499, 7, "Fast"),
        ("ACCE", "Slim Wireless Office Keyboard", "Accessories", "Keyboards", 1100, 1799, 5, "Medium"),
        ("ACCE", "Ergonomic Split Keyboard", "Accessories", "Keyboards", 3500, 5299, 10, "Slow"),
        ("ACCE", "Ergonomic Vertical Mouse", "Accessories", "Mice", 1400, 2199, 6, "Fast"),
        ("ACCE", "Precision Optical Mouse USB", "Accessories", "Mice", 450, 799, 4, "Fast"),
        ("ACCE", "Bluetooth Travel Mouse", "Accessories", "Mice", 850, 1399, 5, "Medium"),
        ("ACCE", "USB-C 7-in-1 Aluminum Dock", "Accessories", "Cables & Docks", 1800, 2899, 7, "Fast"),
        ("ACCE", "Braided 4K HDMI Cable 3M", "Accessories", "Cables & Docks", 350, 699, 4, "Slow"),
        ("ACCE", "Thunderbolt 4 High-Speed Cable", "Accessories", "Cables & Docks", 1200, 1999, 7, "Slow"),
        ("ACCE", "65W GaN Fast Charger 3-Port", "Accessories", "Chargers", 1600, 2499, 5, "Fast"),
        ("ACCE", "100W Laptop USB-C Adapter", "Accessories", "Chargers", 2100, 3199, 7, "Medium"),
        ("ACCE", "Magnetic Wireless Car Charger", "Accessories", "Chargers", 1100, 1799, 6, "Slow"),
        ("ACCE", "Waterproof Laptop Backpack 15", "Accessories", "Bags & Sleeves", 1400, 2299, 7, "Medium"),
        ("ACCE", "Shockproof Laptop Sleeve 14", "Accessories", "Bags & Sleeves", 650, 1199, 5, "Slow"),
        ("ACCE", "Executive Leather Briefcase", "Accessories", "Bags & Sleeves", 3200, 4999, 10, "Slow"),

        # Office Supplies & Tools (15 SKUs)
        ("OFFC", "Ergonomic Mesh Executive Chair", "Office Supplies", "Chairs", 7500, 11500, 12, "Fast"),
        ("OFFC", "High-Back Orthopedic Desk Chair", "Office Supplies", "Chairs", 9800, 14999, 14, "Medium"),
        ("OFFC", "Foldable Training Chair with Pad", "Office Supplies", "Chairs", 2400, 3699, 8, "Slow"),
        ("OFFC", "Magnetic Glass Whiteboard 4x3", "Office Supplies", "Whiteboards", 3200, 4899, 8, "Medium"),
        ("OFFC", "Cross-Cut Document Shredder 15L", "Office Supplies", "Shredders", 4200, 6499, 10, "Medium"),
        ("OFFC", "Dual Monitor Desk Mount Arm", "Office Supplies", "Desk Tools", 2200, 3499, 7, "Fast"),
        ("OFFC", "Aluminum Laptop Stand Riser", "Office Supplies", "Desk Tools", 850, 1499, 5, "Slow"),
        ("OFFC", "Large Desk Blotter Pad Leather", "Office Supplies", "Desk Tools", 650, 1199, 5, "Slow"),
        ("INDU", "Cordless Impact Drill Kit 18V", "Industrial & Tools", "Power Tools", 4800, 7299, 10, "Fast"),
        ("INDU", "Rotary Hammer Drill 800W", "Industrial & Tools", "Power Tools", 6200, 9499, 12, "Medium"),
        ("INDU", "Laser Distance Meter 50M", "Industrial & Tools", "Measuring Tools", 1900, 2999, 6, "Medium"),
        ("INDU", "Digital Multimeter Professional", "Industrial & Tools", "Measuring Tools", 1400, 2299, 6, "Slow"),
        ("INDU", "Industrial Safety Helmet & Visor", "Industrial & Tools", "Safety Gear", 650, 1099, 5, "Slow"),
        ("INDU", "Steel Toe Safety Work Boots", "Industrial & Tools", "Safety Gear", 1800, 2799, 7, "Medium"),
        ("INDU", "Heavy Duty Screwdriver Set 42pc", "Industrial & Tools", "Hand Tools", 850, 1399, 5, "Slow"),
    ]

    products = []
    for idx, item in enumerate(catalog, start=1):
        prefix, name, cat, subcat, cost, price, lead_days, vel = item
        pid = f"P{idx:03d}"
        
        if vel == "Fast":
            daily_demand = random.uniform(8.0, 16.0)
            safety_stock = int(daily_demand * random.uniform(3, 5))
        elif vel == "Medium":
            daily_demand = random.uniform(3.0, 7.0)
            safety_stock = int(daily_demand * random.uniform(4, 6))
        else:
            daily_demand = random.uniform(0.4, 2.0)
            safety_stock = int(max(2, daily_demand * random.uniform(5, 8)))
            
        reorder_point = int(daily_demand * lead_days + safety_stock)

        products.append({
            "product_id": pid,
            "product_name": name,
            "category": cat,
            "subcategory": subcat,
            "unit_cost": cost,
            "selling_price": price,
            "reorder_point": reorder_point,
            "lead_time_days": lead_days,
            "safety_stock": safety_stock,
            "velocity_tier": vel,
            "base_daily_demand": round(daily_demand, 2)
        })

    return pd.DataFrame(products)

# -------------------------------------------------------------------------
# 2. GENERATE 8 STRATEGIC INDIAN SUPPLIERS (Clear Storyline)
# -------------------------------------------------------------------------
def generate_suppliers():
    suppliers = [
        # Stellar Tier 1
        {"supplier_id": "S001", "supplier_name": "Bharat Electronics Ltd", "supplier_region": "Bengaluru Tech Corridor", "supplier_type": "Direct Manufacturer", "contract_start_date": "2021-03-15", "mean_delay": 0.4, "defect_rate": 0.008, "fill_rate": 0.985},
        {"supplier_id": "S002", "supplier_name": "Tata AutoComp Precision Sourcing", "supplier_region": "Pune Industrial Belt", "supplier_type": "Tier-1 Distributor", "contract_start_date": "2020-07-01", "mean_delay": 0.6, "defect_rate": 0.010, "fill_rate": 0.978},
        
        # Reliable Tier 2
        {"supplier_id": "S003", "supplier_name": "Godrej Precision Hardware", "supplier_region": "Mumbai Industrial Zone", "supplier_type": "OEM Manufacturer", "contract_start_date": "2021-11-20", "mean_delay": 1.4, "defect_rate": 0.015, "fill_rate": 0.955},
        {"supplier_id": "S005", "supplier_name": "Havells Components Noida", "supplier_region": "Noida Sector 62 Hub", "supplier_type": "Tier-1 Distributor", "contract_start_date": "2022-01-10", "mean_delay": 1.8, "defect_rate": 0.018, "fill_rate": 0.945},
        {"supplier_id": "S006", "supplier_name": "Lucas-TVS Electrical Hub", "supplier_region": "Chennai Auto Cluster", "supplier_type": "Direct Manufacturer", "contract_start_date": "2021-05-18", "mean_delay": 1.5, "defect_rate": 0.016, "fill_rate": 0.950},
        {"supplier_id": "S008", "supplier_name": "Sanand Microtech Hub", "supplier_region": "Ahmedabad Sanand Hub", "supplier_type": "Regional Supplier", "contract_start_date": "2022-06-01", "mean_delay": 2.1, "defect_rate": 0.022, "fill_rate": 0.935},
        
        # Problem Vendors (Clear Interview Targets!)
        {"supplier_id": "S004", "supplier_name": "Delta Sourcing Logistics India", "supplier_region": "Chennai Sriperumbudur", "supplier_type": "Regional Distributor", "contract_start_date": "2022-08-14", "mean_delay": 5.4, "defect_rate": 0.048, "fill_rate": 0.885},
        {"supplier_id": "S007", "supplier_name": "Krystal Microtech Hyderabad", "supplier_region": "Hyderabad Hardware Park", "supplier_type": "Component Importer", "contract_start_date": "2023-02-10", "mean_delay": 6.8, "defect_rate": 0.056, "fill_rate": 0.825}
    ]
    return pd.DataFrame(suppliers)

# -------------------------------------------------------------------------
# 3. GENERATE 4 KEY REGIONAL HUBS
# -------------------------------------------------------------------------
def generate_warehouses():
    warehouses = [
        {"warehouse_id": "W001", "warehouse_name": "Bengaluru Central Fulfillment Hub", "city": "Bengaluru", "state": "Karnataka", "warehouse_capacity": 60000},
        {"warehouse_id": "W002", "warehouse_name": "Delhi NCR Northern Mega Hub", "city": "Delhi NCR", "state": "Delhi", "warehouse_capacity": 75000},
        {"warehouse_id": "W003", "warehouse_name": "Mumbai Bhiwandi Logistics Depot", "city": "Mumbai", "state": "Maharashtra", "warehouse_capacity": 80000},
        {"warehouse_id": "W004", "warehouse_name": "Chennai Coastal Distribution Center", "city": "Chennai", "state": "Tamil Nadu", "warehouse_capacity": 40000}
    ]
    return pd.DataFrame(warehouses)

# -------------------------------------------------------------------------
# 4. GENERATE 12 MONTHS OF SALES (Clean ~18,000 Records)
# -------------------------------------------------------------------------
def generate_sales(df_products, df_warehouses, start_date="2024-01-01", end_date="2024-12-31"):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end - start).days + 1
    
    warehouses = df_warehouses["warehouse_id"].tolist()
    wh_weights = [0.35, 0.30, 0.22, 0.13] # Bengaluru and Delhi NCR lead
    
    customer_types = ["B2C Retail Customer", "B2B Wholesale Partner", "Corporate Enterprise"]
    cust_weights = [0.70, 0.20, 0.10]
    
    channels = ["Direct Online Portal", "Enterprise Store", "Partner Retail", "National E-Commerce"]
    channel_weights = [0.45, 0.20, 0.20, 0.15]
    
    prod_lookup = df_products.set_index("product_id").to_dict(orient="index")
    pids = list(prod_lookup.keys())
    
    sales_records = []
    sale_counter = 1
    
    weights = np.array([5.0 if prod_lookup[p]["velocity_tier"]=="Fast" else 
                        (2.2 if prod_lookup[p]["velocity_tier"]=="Medium" else 0.5) 
                        for p in pids])
    p_norm = weights / weights.sum()
    
    for day_idx in range(total_days):
        cur_date = start + timedelta(days=day_idx)
        date_str = cur_date.strftime("%Y-%m-%d")
        month = cur_date.month
        day_of_week = cur_date.weekday()
        
        # Indian Festival Seasonality (Navratri, Diwali in Oct-Nov)
        if month in [10, 11]:
            season_mult = 1.65
        elif month == 12:
            season_mult = 1.25
        elif month in [1, 2]:
            season_mult = 0.85
        elif month in [6, 7]:
            season_mult = 1.15
        else:
            season_mult = 1.0
            
        is_weekend = day_of_week in [5, 6]
        day_mult = 1.20 if is_weekend else 0.95
        
        daily_tx = np.random.poisson(int(45 * season_mult * day_mult))
        sampled_pids = np.random.choice(pids, size=daily_tx, replace=True, p=p_norm)
        
        for pid in sampled_pids:
            p_info = prod_lookup[pid]
            wh = np.random.choice(warehouses, p=wh_weights)
            cust = np.random.choice(customer_types, p=cust_weights)
            chan = np.random.choice(channels, p=channel_weights)
            
            if cust == "B2B Wholesale Partner":
                qty = max(4, int(np.random.exponential(scale=12)))
                discount = 0.88
            elif cust == "Corporate Enterprise":
                qty = max(2, int(np.random.exponential(scale=8)))
                discount = 0.92
            else:
                qty = max(1, int(np.random.geometric(p=0.55)))
                discount = 1.0
                
            unit_price = round(p_info["selling_price"] * discount, 2)
            
            sales_records.append({
                "sale_id": f"SAL{sale_counter:06d}",
                "sale_date": date_str,
                "product_id": pid,
                "warehouse_id": wh,
                "quantity_sold": qty,
                "unit_price": unit_price,
                "customer_type": cust,
                "sales_channel": chan
            })
            sale_counter += 1

    return pd.DataFrame(sales_records)

# -------------------------------------------------------------------------
# 5. GENERATE POs & DELIVERIES
# -------------------------------------------------------------------------
def generate_purchase_orders_and_deliveries(df_products, df_suppliers, df_warehouses, df_sales, start_date="2024-01-01", end_date="2024-12-31"):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    supplier_ids = df_suppliers["supplier_id"].tolist()
    supplier_lookup = df_suppliers.set_index("supplier_id").to_dict(orient="index")
    prod_lookup = df_products.set_index("product_id").to_dict(orient="index")
    
    product_suppliers = {}
    for pid in prod_lookup:
        # Deliberately map problem products to S004 and S007 to illustrate the case study!
        if pid in ["P001", "P004", "P016"]: # Laptops & Air Purifiers
            product_suppliers[pid] = "S007" if pid == "P001" else "S004"
        else:
            product_suppliers[pid] = random.choice(supplier_ids)

    sales_agg = df_sales.groupby(["product_id", "warehouse_id"])["quantity_sold"].sum().reset_index()
    
    po_records = []
    deliv_records = []
    po_counter = 1
    deliv_counter = 1
    
    for _, row in sales_agg.iterrows():
        pid = row["product_id"]
        wid = row["warehouse_id"]
        total_sold = row["quantity_sold"]
        p_info = prod_lookup[pid]
        sid = product_suppliers[pid]
        s_profile = supplier_lookup[sid]
        
        num_orders = random.randint(8, 14) if p_info["velocity_tier"] == "Fast" else (random.randint(5, 9) if p_info["velocity_tier"] == "Medium" else random.randint(3, 5))
        avg_order_qty = max(5, int(total_sold / num_orders * random.uniform(0.95, 1.15)))
        
        days_span = (end - start).days
        order_day_offsets = sorted(random.sample(range(5, days_span - 15), min(num_orders, days_span - 25)))
        
        for day_offset in order_day_offsets:
            po_date_dt = start + timedelta(days=day_offset)
            ordered_qty = max(5, int(avg_order_qty * random.uniform(0.85, 1.25)))
            
            lead_time = p_info["lead_time_days"]
            exp_dt = po_date_dt + timedelta(days=lead_time)
            disp_dt = po_date_dt + timedelta(days=random.randint(1, 2))
            
            delay = int(round(np.random.normal(s_profile["mean_delay"], 1.5)))
            delay = max(-1, delay)
            act_dt = exp_dt + timedelta(days=delay)
            
            fill = min(1.0, max(0.60, s_profile["fill_rate"] + random.uniform(-0.03, 0.01)))
            qty_rec = int(round(ordered_qty * fill))
            defect = max(0.0, s_profile["defect_rate"] + random.uniform(-0.005, 0.01))
            qty_dmg = int(round(qty_rec * defect))
            
            po_id = f"PO{po_counter:05d}"
            deliv_id = f"DEL{deliv_counter:05d}"
            
            po_records.append({
                "po_id": po_id,
                "po_date": po_date_dt.strftime("%Y-%m-%d"),
                "supplier_id": sid,
                "product_id": pid,
                "warehouse_id": wid,
                "ordered_quantity": ordered_qty,
                "expected_delivery_date": exp_dt.strftime("%Y-%m-%d"),
                "actual_delivery_date": act_dt.strftime("%Y-%m-%d"),
                "unit_cost": p_info["unit_cost"]
            })
            
            deliv_records.append({
                "delivery_id": deliv_id,
                "po_id": po_id,
                "supplier_id": sid,
                "product_id": pid,
                "warehouse_id": wid,
                "dispatch_date": disp_dt.strftime("%Y-%m-%d"),
                "expected_delivery_date": exp_dt.strftime("%Y-%m-%d"),
                "actual_delivery_date": act_dt.strftime("%Y-%m-%d"),
                "quantity_ordered": ordered_qty,
                "quantity_received": qty_rec,
                "damaged_quantity": qty_dmg
            })
            
            po_counter += 1
            deliv_counter += 1

    return pd.DataFrame(po_records), pd.DataFrame(deliv_records)

# -------------------------------------------------------------------------
# 6. GENERATE INVENTORY (Strict Conservation Law)
# -------------------------------------------------------------------------
def generate_inventory(df_products, df_warehouses, df_sales, df_deliveries, start_date="2024-01-01", end_date="2024-12-31"):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end - start).days + 1
    
    sales_map = df_sales.groupby(["sale_date", "product_id", "warehouse_id"])["quantity_sold"].sum().to_dict()
    deliv_rec_map = df_deliveries.groupby(["actual_delivery_date", "product_id", "warehouse_id"])["quantity_received"].sum().to_dict()
    deliv_dmg_map = df_deliveries.groupby(["actual_delivery_date", "product_id", "warehouse_id"])["damaged_quantity"].sum().to_dict()
    
    prod_lookup = df_products.set_index("product_id").to_dict(orient="index")
    warehouse_ids = df_warehouses["warehouse_id"].tolist()
    
    current_inventory = {}
    for pid, p_info in prod_lookup.items():
        for wid in warehouse_ids:
            if p_info["velocity_tier"] == "Fast":
                init_stock = int(p_info["reorder_point"] * random.uniform(0.7, 1.2))
            elif p_info["velocity_tier"] == "Medium":
                init_stock = int(p_info["reorder_point"] * random.uniform(1.0, 1.8))
            else:
                init_stock = int(p_info["reorder_point"] * random.uniform(2.5, 4.0)) # Intentional excess
            current_inventory[(pid, wid)] = max(5, init_stock)
            
    inventory_records = []
    pids = list(prod_lookup.keys())
    
    for day_idx in range(total_days):
        cur_date = start + timedelta(days=day_idx)
        date_str = cur_date.strftime("%Y-%m-%d")
        is_weekly = (day_idx % 7 == 0) or (day_idx == total_days - 1)
        
        for pid in pids:
            for wid in warehouse_ids:
                opening = current_inventory[(pid, wid)]
                sold = sales_map.get((date_str, pid, wid), 0)
                received = deliv_rec_map.get((date_str, pid, wid), 0)
                damaged = deliv_dmg_map.get((date_str, pid, wid), 0)
                
                available = opening + received - damaged
                actual_sold = min(sold, max(0, available))
                closing = max(0, opening + received - actual_sold - damaged)
                current_inventory[(pid, wid)] = closing
                
                # Record weekly snapshots or daily for key cohorts
                if is_weekly or pid in pids[:20]:
                    inventory_records.append({
                        "inventory_date": date_str,
                        "product_id": pid,
                        "warehouse_id": wid,
                        "opening_stock": opening,
                        "stock_received": received,
                        "quantity_sold": actual_sold,
                        "damaged_stock": damaged,
                        "closing_stock": closing
                    })

    return pd.DataFrame(inventory_records)

# -------------------------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------------------------
def main():
    print("=" * 75)
    print("GENERATING CRISP, INTERVIEW-OPTIMIZED SUPPLY CHAIN DATASET (INDIA - INR)")
    print("=" * 75)
    
    print("\n[1/5] Generating 60 Relatable Indian Products...")
    df_products = generate_products()
    products_file = os.path.join(OUTPUT_DIR, "products.csv")
    df_products[["product_id", "product_name", "category", "subcategory", "unit_cost", "selling_price", "reorder_point", "lead_time_days", "safety_stock"]].to_csv(products_file, index=False)
    print(f" -> Saved: {products_file} (60 items across 4 categories)")
    
    print("\n[2/5] Generating 8 Strategic Indian Suppliers...")
    df_suppliers = generate_suppliers()
    suppliers_file = os.path.join(OUTPUT_DIR, "suppliers.csv")
    df_suppliers[["supplier_id", "supplier_name", "supplier_region", "supplier_type", "contract_start_date"]].to_csv(suppliers_file, index=False)
    print(f" -> Saved: {suppliers_file} (8 strategic vendor partners)")
    
    print("\n[3/5] Generating 4 Regional Distribution Hubs...")
    df_warehouses = generate_warehouses()
    warehouses_file = os.path.join(OUTPUT_DIR, "warehouses.csv")
    df_warehouses.to_csv(warehouses_file, index=False)
    print(f" -> Saved: {warehouses_file} (Bengaluru, Delhi NCR, Mumbai, Chennai)")
    
    print("\n[4/5] Generating 12 Months of Clean Sales Transactions...")
    df_sales = generate_sales(df_products, df_warehouses, start_date="2024-01-01", end_date="2024-12-31")
    sales_file = os.path.join(OUTPUT_DIR, "sales.csv")
    df_sales.to_csv(sales_file, index=False)
    print(f" -> Saved: {sales_file} ({len(df_sales):,} clean transaction rows)")
    
    print("\n[5/5] Generating Purchase Orders, Deliveries, and Inventory...")
    df_po, df_deliveries = generate_purchase_orders_and_deliveries(df_products, df_suppliers, df_warehouses, df_sales)
    po_file = os.path.join(OUTPUT_DIR, "purchase_orders.csv")
    df_po.to_csv(po_file, index=False)
    print(f" -> Saved: {po_file} ({len(df_po):,} PO records)")
    
    deliv_file = os.path.join(OUTPUT_DIR, "deliveries.csv")
    df_deliveries.to_csv(deliv_file, index=False)
    print(f" -> Saved: {deliv_file} ({len(df_deliveries):,} delivery records)")
    
    df_inventory = generate_inventory(df_products, df_warehouses, df_sales, df_deliveries)
    inv_file = os.path.join(OUTPUT_DIR, "inventory.csv")
    df_inventory.to_csv(inv_file, index=False)
    print(f" -> Saved: {inv_file} ({len(df_inventory):,} inventory snapshot rows)")
    
    print("\n" + "=" * 75)
    print("STREAMLINED DATASET GENERATION COMPLETED SUCCESSFULLY!")
    print("=" * 75)

if __name__ == "__main__":
    main()
