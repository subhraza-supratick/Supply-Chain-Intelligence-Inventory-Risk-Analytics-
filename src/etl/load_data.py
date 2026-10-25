"""
Load Data Module.
Handles loading raw data from CSV files and establishing database connectivity for PostgreSQL and SQLite.
"""

import os
import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def load_raw_csvs(data_dir=RAW_DATA_DIR):
    """
    Loads all raw CSV files into a dictionary of pandas DataFrames.
    """
    files = {
        "products": "products.csv",
        "suppliers": "suppliers.csv",
        "warehouses": "warehouses.csv",
        "sales": "sales.csv",
        "inventory": "inventory.csv",
        "purchase_orders": "purchase_orders.csv",
        "deliveries": "deliveries.csv"
    }
    
    data = {}
    for name, fname in files.items():
        fpath = os.path.join(data_dir, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Raw data file not found: {fpath}. Please run generate_data.py first.")
        print(f"Loading {fname}...")
        data[name] = pd.read_csv(fpath)
        print(f" -> Loaded {name}: {data[name].shape[0]:,} rows, {data[name].shape[1]} columns")
        
    return data

def get_db_engine(db_type="sqlite", connection_string=None):
    """
    Creates and returns a SQLAlchemy engine.
    Defaults to a local SQLite database in data/processed/supply_chain.db for zero-config execution.
    Can be configured for PostgreSQL via connection_string (e.g. 'postgresql://user:pass@localhost:5432/supply_chain_dw').
    """
    if db_type == "sqlite" or connection_string is None:
        db_path = os.path.join(PROCESSED_DATA_DIR, "supply_chain.db")
        engine = create_engine(f"sqlite:///{db_path}")
    else:
        engine = create_engine(connection_string)
    return engine

def save_to_db(data_dict, engine):
    """
    Saves a dictionary of DataFrames into the database.
    """
    for table_name, df in data_dict.items():
        print(f"Writing table '{table_name}' to database ({len(df):,} rows)...")
        df.to_sql(table_name, engine, if_exists="replace", index=False)
    print("Database write complete.")
