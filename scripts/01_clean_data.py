"""
Growify Digital — XYZ Luxury Assessment
Step 1: Data Cleaning

Takes the three raw exports (Shopify, Google Ads, Meta Ads) and produces
analysis-ready CSVs in data/cleaned/. This is the same cleaning that feeds
the Power BI / Looker Studio model and the SQLite database in step 2.

Run: python scripts/01_clean_data.py
"""

import pandas as pd
import numpy as np
import os

RAW = "data/raw"
CLEAN = "data/cleaned"
os.makedirs(CLEAN, exist_ok=True)


def clean_shopify():
    df = pd.read_csv(f"{RAW}/Shopify_sales_data.csv")

    # Standardise date
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")

    # Numeric columns that may contain blanks / non-numeric junk
    numeric_cols = [
        "Gross Sales (INR)", "Net Sales (INR)", "Total Sales (INR)", "Orders",
        "Returns (INR)", "Return Rate", "Items Sold", "Items Returned",
        "Average Order Value (INR)", "New Customer Orders",
        "Returning Customer Orders", "Average Items Per Order",
        "Discounts (INR)", "Row Count",
    ]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # Drop rows with no date at all — unusable for time-series analysis
    df = df.dropna(subset=["Date"])

    # Normalise blank traffic source to an explicit "Untagged" bucket
    # rather than leaving nulls, since Shopify's own tagging is incomplete
    # (see README — ~42% of net sales carry no traffic-source tag).
    df["Shopify Traffic Source"] = df["Shopify Traffic Source"].fillna("Untagged")
    df.loc[df["Shopify Traffic Source"].str.strip() == "", "Shopify Traffic Source"] = "Untagged"

    # Standardise text fields
    for c in ["Sales Channel", "Product Title", "Billing Province", "Billing City"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    out = f"{CLEAN}/shopify_clean.csv"
    df.to_csv(out, index=False)
    print(f"Shopify: {len(df):,} rows -> {out}")
    return df


def clean_google():
    df = pd.read_csv(f"{RAW}/Google_Ads_data.csv")
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
    df = df.dropna(subset=["Date"])

    numeric_cols = ["Cost (INR)", "Clicks", "Impressions", "CPC (INR)", "CTR",
                     "CPM (INR)", "Conversions", "Conv. Value (INR)"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["Campaign"] = df["Campaign"].astype(str).str.strip()
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    # Derived fields used throughout the analysis
    df["ROAS"] = np.where(df["Cost (INR)"] > 0, df["Conv. Value (INR)"] / df["Cost (INR)"], 0)

    out = f"{CLEAN}/google_ads_clean.csv"
    df.to_csv(out, index=False)
    print(f"Google Ads: {len(df):,} rows -> {out}")
    return df


def clean_facebook():
    df = pd.read_csv(f"{RAW}/Facebook_Ads_data.csv")
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
    df = df.dropna(subset=["Date"])

    numeric_cols = [
        "Amount Spent (INR)", "Clicks (all)", "Impressions", "Link Clicks",
        "Purchases", "Purchases Conversion Value (INR)", "Adds to Cart",
        "Checkouts Initiated", "Adds of Payment Info",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    for c in ["Campaign Name", "Ad Set Name", "Ad Name", "Country"]:
        df[c] = df[c].astype(str).str.strip()

    # Drop the heavy creative-asset URL columns — not needed for analysis,
    # and they roughly triple the file size for no analytical value.
    drop_cols = [c for c in df.columns if "Permalink" in c or "Thumbnail" in c or "Picture URL" in c or "Shareable Link" in c]
    df = df.drop(columns=drop_cols, errors="ignore")

    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["ROAS"] = np.where(
        df["Amount Spent (INR)"] > 0,
        df["Purchases Conversion Value (INR)"] / df["Amount Spent (INR)"],
        0,
    )

    out = f"{CLEAN}/facebook_ads_clean.csv"
    df.to_csv(out, index=False)
    print(f"Facebook Ads: {len(df):,} rows -> {out}")
    return df


def build_unified_ads(g, f):
    """Platform-agnostic fact table for the 'Channel Performance' BI page."""
    g_u = g.groupby(["Date", "Month", "Campaign", "Country"], as_index=False).agg(
        Spend=("Cost (INR)", "sum"),
        Revenue=("Conv. Value (INR)", "sum"),
        Conversions=("Conversions", "sum"),
        Clicks=("Clicks", "sum"),
        Impressions=("Impressions", "sum"),
    )
    g_u["Platform"] = "Google"

    f_u = f.groupby(["Date", "Month", "Campaign Name", "Country"], as_index=False).agg(
        Spend=("Amount Spent (INR)", "sum"),
        Revenue=("Purchases Conversion Value (INR)", "sum"),
        Conversions=("Purchases", "sum"),
        Clicks=("Link Clicks", "sum"),
        Impressions=("Impressions", "sum"),
    )
    f_u = f_u.rename(columns={"Campaign Name": "Campaign"})
    f_u["Platform"] = "Meta"

    unified = pd.concat([g_u, f_u], ignore_index=True)
    unified["ROAS"] = np.where(unified["Spend"] > 0, unified["Revenue"] / unified["Spend"], 0)

    out = f"{CLEAN}/unified_ads_clean.csv"
    unified.to_csv(out, index=False)
    print(f"Unified ads fact table: {len(unified):,} rows -> {out}")
    return unified


if __name__ == "__main__":
    sh = clean_shopify()
    g = clean_google()
    f = clean_facebook()
    build_unified_ads(g, f)
    print("\nDone. Cleaned files are in data/cleaned/ — import these into Power BI / Looker Studio.")
