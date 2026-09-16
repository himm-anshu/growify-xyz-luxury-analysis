# XYZ Luxury — Marketing Performance Analysis & 25% Growth Plan

**Growify Digital · Associate Data Analyst Candidate Assessment**

Full analysis of 6 months (Mar–Aug 2026) of Shopify, Google Ads, and Meta Ads
data for XYZ Luxury, a D2C jewellery/accessories brand, against a single
objective: **grow sales 25% without increasing marketing budget.**

---

## Headline finding

Blended ad-platform ROAS fell from **3.09x in April to 1.59x in August**,
even as spend rose — driven by two campaigns (46% of total budget) that were
scaled straight into audience saturation. The account isn't short of budget;
it's short of discipline in where that budget goes. Full breakdown in the
written analysis and reproducible in SQL below.

## Repo structure

```
├── data/
│   ├── raw/              # Original exports, unmodified
│   ├── cleaned/           # Cleaned, analysis-ready CSVs (output of scripts/01)
│   └── xyz_luxury.db      # SQLite DB built from the cleaned CSVs (output of scripts/02)
├── scripts/
│   ├── 01_clean_data.py   # Cleans dates, types, nulls; builds unified ads fact table
│   ├── 02_build_sqlite.py # Loads cleaned CSVs into SQLite (zero setup, no server needed)
│   └── 02_build_mysql.py  # Loads cleaned CSVs into MySQL (set DB_USER/DB_PASS/DB_HOST env vars)
├── sql/
│   ├── queries.sql        # 13 queries, SQLite syntax — reproduces every key number in the written analysis
│   └── queries_mysql.sql  # Same 13 queries, MySQL/MariaDB syntax (backtick-quoted identifiers)
├── docs/
│   └── XYZ_Luxury_Growify_Analysis.docx   # Full written analysis (all assessment sections)
├── powerbi/
│   └── README.md          # Data model, DAX measures, and page-by-page build spec
└── requirements.txt
```

## How to reproduce this analysis

```bash
pip install -r requirements.txt
python scripts/01_clean_data.py      # -> data/cleaned/*.csv
```

**Option A — SQLite (no server setup needed):**
```bash
python scripts/02_build_sqlite.py    # -> data/xyz_luxury.db
sqlite3 data/xyz_luxury.db < sql/queries.sql
```

**Option B — MySQL:**
```bash
# create a database first: CREATE DATABASE xyz_luxury;
export DB_USER=youruser DB_PASS=yourpass DB_HOST=localhost DB_PORT=3306 DB_NAME=xyz_luxury
python scripts/02_build_mysql.py
mysql -u youruser -p xyz_luxury < sql/queries_mysql.sql
```
Both were tested end-to-end and return identical results.

## Data quality note

Shopify's own traffic-source tagging covers only a small fraction of net
sales (~2%) — the rest is `Untagged`. This means ad-platform "Conv. Value"
figures used throughout this analysis are the platforms' own pixel-based
attribution, not a verified order-level match to Shopify. All ROAS figures
are directionally reliable and internally consistent for comparison, but
not a reconciled P&L. This is flagged wherever it materially affects a
conclusion, particularly in the 25%-growth feasibility section.

## Deliverables

| Requirement | Where |
|---|---|
| Marketing performance analysis & diagnosis | `docs/XYZ_Luxury_Growify_Analysis.docx`, Sections 1–2 |
| Campaign → Ad Set → Ad audit | Section 2; reproducible via `sql/queries.sql` Q5–Q8 |
| Budget reallocation plan | Section 3 (named campaigns, totals unchanged) |
| Why the brand isn't scaling | Section 4 |
| 25% growth strategy & feasibility | Section 5 |
| BI report data model, DAX, page spec | Section 6 and `powerbi/README.md` |
| Management summary | Section 7 |
| Power BI / Looker Studio file | *(built separately — see `powerbi/README.md`; link/file added once complete)* |

## Tools

Python (pandas) for cleaning · SQLite for querying · Power BI / Looker Studio
for the dashboard · Microsoft Word for the written report.
