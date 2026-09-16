"""
Growify Digital — XYZ Luxury Assessment
Step 2: Load cleaned data into a SQLite database so the analysis can be
run with SQL (see sql/queries.sql).

Run: python scripts/02_build_sqlite.py
"""

import sqlite3
import pandas as pd
import os

CLEAN = "data/cleaned"
DB = "data/xyz_luxury.db"

if os.path.exists(DB):
    os.remove(DB)

conn = sqlite3.connect(DB)

tables = {
    "shopify_sales": "shopify_clean.csv",
    "google_ads": "google_ads_clean.csv",
    "facebook_ads": "facebook_ads_clean.csv",
    "unified_ads": "unified_ads_clean.csv",
}

for table_name, filename in tables.items():
    df = pd.read_csv(f"{CLEAN}/{filename}")
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded {len(df):,} rows into '{table_name}'")

conn.commit()
conn.close()
print(f"\nDatabase built at {DB}")
