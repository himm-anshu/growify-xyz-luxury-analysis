"""
Growify Digital — XYZ Luxury Assessment
Step 2 (MySQL version): Load cleaned CSVs into a MySQL database.

Set connection details via environment variables, or edit the defaults below.
Requires: pip install pandas sqlalchemy pymysql

Run: python scripts/02_build_mysql.py
"""

import os
import pandas as pd
from sqlalchemy import create_engine

CLEAN = "data/cleaned"

DB_USER = os.environ.get("DB_USER", "growify")
DB_PASS = os.environ.get("DB_PASS", "growify123")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "xyz_luxury")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

tables = {
    "shopify_sales": "shopify_clean.csv",
    "google_ads": "google_ads_clean.csv",
    "facebook_ads": "facebook_ads_clean.csv",
    "unified_ads": "unified_ads_clean.csv",
}

for table_name, filename in tables.items():
    df = pd.read_csv(f"{CLEAN}/{filename}")
    df.to_sql(table_name, engine, if_exists="replace", index=False, chunksize=1000)
    print(f"Loaded {len(df):,} rows into '{table_name}'")

print(f"\nDone. Database '{DB_NAME}' is ready — run sql/queries_mysql.sql against it.")
