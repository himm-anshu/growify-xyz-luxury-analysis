-- ============================================================
-- Growify Digital — XYZ Luxury Assessment
-- SQL Analysis Queries (MySQL / MariaDB version)
-- Run against the `xyz_luxury` database built by scripts/02_build_mysql.py
-- These queries reproduce the key numbers behind docs/XYZ_Luxury_Growify_Analysis.docx
-- ============================================================


-- ------------------------------------------------------------
-- 1. Platform-level performance (Section 1.1)
-- ------------------------------------------------------------
SELECT
    Platform,
    ROUND(SUM(Spend), 0)      AS total_spend,
    ROUND(SUM(Revenue), 0)    AS total_revenue,
    ROUND(SUM(Revenue) * 1.0 / NULLIF(SUM(Spend), 0), 2) AS roas,
    ROUND(SUM(Clicks) * 100.0 / NULLIF(SUM(Impressions), 0), 2) AS ctr_pct
FROM unified_ads
GROUP BY Platform
ORDER BY total_spend DESC;


-- ------------------------------------------------------------
-- 2. Monthly blended ROAS trend (Section 1.2 — the core finding)
-- ------------------------------------------------------------
SELECT
    Month,
    ROUND(SUM(Spend), 0)   AS total_spend,
    ROUND(SUM(Revenue), 0) AS total_revenue,
    ROUND(SUM(Revenue) * 1.0 / NULLIF(SUM(Spend), 0), 2) AS blended_roas
FROM unified_ads
GROUP BY Month
ORDER BY Month;


-- ------------------------------------------------------------
-- 3. Business-level ROAS: Shopify net sales vs total ad spend (Section 1.3)
-- ------------------------------------------------------------
SELECT
    (SELECT ROUND(SUM(`Net Sales (INR)`), 0) FROM shopify_sales) AS shopify_net_sales,
    (SELECT ROUND(SUM(Spend), 0) FROM unified_ads)                AS total_ad_spend,
    ROUND(
        (SELECT SUM(`Net Sales (INR)`) FROM shopify_sales) * 1.0
        / NULLIF((SELECT SUM(Spend) FROM unified_ads), 0)
    , 2) AS business_roas;


-- ------------------------------------------------------------
-- 4. Shopify traffic-source coverage (data-quality / attribution-gap check)
-- ------------------------------------------------------------
SELECT
    `Shopify Traffic Source` AS traffic_source,
    COUNT(*)                 AS orders,
    ROUND(SUM(`Net Sales (INR)`), 0) AS net_sales
FROM shopify_sales
GROUP BY traffic_source
ORDER BY net_sales DESC;


-- ------------------------------------------------------------
-- 5. Campaign-level audit — all campaigns ranked by spend (Section 2.1)
-- ------------------------------------------------------------
SELECT
    Platform,
    Campaign,
    ROUND(SUM(Spend), 0)   AS spend,
    ROUND(SUM(Revenue), 0) AS revenue,
    ROUND(SUM(Revenue) * 1.0 / NULLIF(SUM(Spend), 0), 2) AS roas,
    SUM(Conversions) AS conversions,
    CASE
        WHEN SUM(Spend) = 0 THEN 'N/A'
        WHEN SUM(Revenue) = 0 THEN 'KILL — zero return'
        WHEN SUM(Revenue) * 1.0 / SUM(Spend) >= 2.0 THEN 'WINNER — scale'
        WHEN SUM(Revenue) * 1.0 / SUM(Spend) < 1.2 THEN 'LOSER — reduce'
        ELSE 'MAINTAIN'
    END AS verdict
FROM unified_ads
GROUP BY Platform, Campaign
ORDER BY spend DESC;


-- ------------------------------------------------------------
-- 6. Saturation check — monthly ROAS trend for the two largest campaigns
--    (Section 2.2 — proves the `scaled too fast` pattern)
-- ------------------------------------------------------------
SELECT
    Campaign,
    Month,
    ROUND(SUM(Spend), 0)   AS spend,
    ROUND(SUM(Revenue), 0) AS revenue,
    ROUND(SUM(Revenue) * 1.0 / NULLIF(SUM(Spend), 0), 2) AS roas
FROM unified_ads
WHERE Campaign IN (
    'Conv | Tof | Multi Category | Ind | Direct | Growify |',
    'Growify | MOF & BOF | Sale | India +intl'
)
GROUP BY Campaign, Month
ORDER BY Campaign, Month;


-- ------------------------------------------------------------
-- 7. Ad Set level audit — Meta only (Section 2, `granularity` requirement)
-- ------------------------------------------------------------
SELECT
    `Campaign Name` AS campaign,
    `Ad Set Name`    AS ad_set,
    ROUND(SUM(`Amount Spent (INR)`), 0) AS spend,
    ROUND(SUM(`Purchases Conversion Value (INR)`), 0) AS revenue,
    ROUND(SUM(`Purchases Conversion Value (INR)`) * 1.0
          / NULLIF(SUM(`Amount Spent (INR)`), 0), 2) AS roas
FROM facebook_ads
GROUP BY campaign, ad_set
ORDER BY spend DESC
LIMIT 20;


-- ------------------------------------------------------------
-- 8. Ad / creative level audit — Meta only
-- ------------------------------------------------------------
SELECT
    `Campaign Name` AS campaign,
    `Ad Name`        AS ad_creative,
    ROUND(SUM(`Amount Spent (INR)`), 0) AS spend,
    ROUND(SUM(`Purchases Conversion Value (INR)`), 0) AS revenue,
    ROUND(SUM(`Purchases Conversion Value (INR)`) * 1.0
          / NULLIF(SUM(`Amount Spent (INR)`), 0), 2) AS roas
FROM facebook_ads
GROUP BY campaign, ad_creative
ORDER BY spend DESC
LIMIT 20;


-- ------------------------------------------------------------
-- 9. Zero-return spend — campaigns to kill (Section 4, Reason 2)
-- ------------------------------------------------------------
SELECT
    Platform,
    Campaign,
    ROUND(SUM(Spend), 0) AS wasted_spend
FROM unified_ads
GROUP BY Platform, Campaign
HAVING SUM(Revenue) = 0 AND SUM(Spend) > 0
ORDER BY wasted_spend DESC;


-- ------------------------------------------------------------
-- 10. New vs returning customers (Section 1.4 / Section 4, Reason 3)
-- ------------------------------------------------------------
SELECT
    SUM(`New Customer Orders`)       AS new_customer_orders,
    SUM(`Returning Customer Orders`) AS returning_customer_orders,
    ROUND(
        SUM(`Returning Customer Orders`) * 100.0
        / NULLIF(SUM(`New Customer Orders`) + SUM(`Returning Customer Orders`), 0)
    , 1) AS returning_pct
FROM shopify_sales;


-- ------------------------------------------------------------
-- 11. Top products by net sales
-- ------------------------------------------------------------
SELECT
    `Product Title` AS product,
    ROUND(SUM(`Net Sales (INR)`), 0) AS net_sales,
    SUM(Orders) AS orders
FROM shopify_sales
WHERE `Product Title` IS NOT NULL AND `Product Title` != 'nan'
GROUP BY product
ORDER BY net_sales DESC
LIMIT 10;


-- ------------------------------------------------------------
-- 12. Country / geo performance split (Meta)
-- ------------------------------------------------------------
SELECT
    Country,
    ROUND(SUM(`Amount Spent (INR)`), 0) AS spend,
    ROUND(SUM(`Purchases Conversion Value (INR)`), 0) AS revenue,
    ROUND(SUM(`Purchases Conversion Value (INR)`) * 1.0
          / NULLIF(SUM(`Amount Spent (INR)`), 0), 2) AS roas
FROM facebook_ads
GROUP BY Country
ORDER BY spend DESC;


-- ------------------------------------------------------------
-- 13. The 25% growth target — required ROAS math (Section 5.1)
-- ------------------------------------------------------------
SELECT
    ROUND((SELECT SUM(`Net Sales (INR)`) FROM shopify_sales), 0) AS current_sales,
    ROUND((SELECT SUM(`Net Sales (INR)`) FROM shopify_sales) * 1.25, 0) AS target_sales,
    ROUND((SELECT SUM(Spend) FROM unified_ads), 0) AS current_spend,
    ROUND(
        (SELECT SUM(`Net Sales (INR)`) FROM shopify_sales) * 1.0
        / NULLIF((SELECT SUM(Spend) FROM unified_ads), 0)
    , 2) AS current_roas,
    ROUND(
        (SELECT SUM(`Net Sales (INR)`) FROM shopify_sales) * 1.25
        / NULLIF((SELECT SUM(Spend) FROM unified_ads), 0)
    , 2) AS required_roas;
