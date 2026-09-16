# Power BI / Looker Studio Build Guide

This folder is where the finished `.pbix` file (or a Looker Studio share
link, pasted into this file) goes once built. Below is the full spec used
to build it — data model, DAX measures, and page-by-page layout — taken
from Section 6 of the written analysis.

## 1. Import

Import the four files in `data/cleaned/`:
- `shopify_clean.csv` → table `Fact_Shopify`
- `google_ads_clean.csv` → table `Fact_Google`
- `facebook_ads_clean.csv` → table `Fact_Meta`
- `unified_ads_clean.csv` → table `Fact_Ads_Unified` (pre-built Google+Meta union — use this for any platform-agnostic visual)

## 2. Data model

- Add a standard `Dim_Date` table, mark it as the official Date table.
- Relate `Dim_Date[Date]` (1) → (*) `Date` column on every fact table.
- **Do not** relate `Fact_Shopify` directly to `Fact_Google`/`Fact_Meta`/`Fact_Ads_Unified`
  — there is no reliable order-level join key between Shopify and the ad
  platforms in this data (see main README's Data Quality note). Blended /
  business-level ROAS is built as a measure that independently sums each
  table, not via a merged relationship.

## 3. Core DAX measures

```
Total Spend            = SUM(Fact_Ads_Unified[Spend])
Total Ad Revenue       = SUM(Fact_Ads_Unified[Revenue])
Platform ROAS          = DIVIDE([Total Ad Revenue], [Total Spend], 0)
Shopify Net Sales      = SUM(Fact_Shopify[Net Sales (INR)])
Business ROAS          = DIVIDE([Shopify Net Sales], [Total Spend], 0)
CTR                    = DIVIDE(SUM(Fact_Ads_Unified[Clicks]), SUM(Fact_Ads_Unified[Impressions]), 0)
CPC                    = DIVIDE([Total Spend], SUM(Fact_Ads_Unified[Clicks]), 0)
CPM                    = DIVIDE([Total Spend], SUM(Fact_Ads_Unified[Impressions]), 0) * 1000
Conversion Rate        = DIVIDE(SUM(Fact_Ads_Unified[Conversions]), SUM(Fact_Ads_Unified[Clicks]), 0)
AOV                    = DIVIDE([Shopify Net Sales], SUM(Fact_Shopify[Orders]), 0)
Returning Customer %   = DIVIDE(SUM(Fact_Shopify[Returning Customer Orders]), SUM(Fact_Shopify[Orders]), 0)
Required ROAS for +25% = DIVIDE([Shopify Net Sales] * 1.25, [Total Spend], 0)

MoM ROAS =
VAR PrevMonth = CALCULATE([Platform ROAS], DATEADD(Dim_Date[Date], -1, MONTH))
RETURN DIVIDE([Platform ROAS] - PrevMonth, PrevMonth, 0)
```

## 4. Pages

| # | Page | Key visuals |
|---|---|---|
| 1 | Executive Overview | KPI cards (Spend, Ad Revenue, Business ROAS, Orders); Spend vs Sales trend; ROAS trend with a target line at 4.58x |
| 2 | Channel / Platform Performance | Google vs Meta: Spend, ROAS, CTR, CPC, CPM bars; spend-share vs ROAS-share scatter |
| 3 | Campaign Performance | Campaign table, conditional-formatted ROAS; spend-vs-ROAS scatter, bubble size = revenue |
| 4 | Ad Set & Ad Deep Dive | Drill-through from Campaign; ROAS-over-time small multiples per ad set (surfaces saturation curves) |
| 5 | Funnel & Efficiency | CTR/CPC/CPM trend; conversion rate by campaign; new vs returning customer split |
| 6 | Budget Reallocation & Growth Plan | Current vs proposed spend waterfall by campaign; required-ROAS gauge vs current |
| 7 | Management Summary | Static text/card layout mirroring Section 7 of the written analysis |

Slicers on every page: Date range, Platform, Country/Geo.

## 5. Once built

- Export a PDF of the finished report and drop it in this folder (or link it).
- If using Looker Studio instead, delete this file's Power BI framing and
  paste the view-access share link here.
