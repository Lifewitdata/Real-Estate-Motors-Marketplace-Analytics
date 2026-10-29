-- DuckDB tables `screened_sales` and `class_lookup` are loaded by the pipeline.
CREATE OR REPLACE TABLE research_sales AS
SELECT s.*, c.class_description
FROM screened_sales s JOIN class_lookup c
 ON s.building_class_at_time_of_sale=c.class_code
WHERE s.eligible;

CREATE OR REPLACE TABLE neighborhood_summary AS
SELECT neighborhood,building_class_at_time_of_sale,class_description,
 COUNT(*) AS sales, SUM(sale_price) AS recorded_consideration,
 MEDIAN(sale_price) AS median_price, MEDIAN(price_per_sqft) AS median_ppsf,
 QUANTILE_CONT(price_per_sqft,0.25) AS q25_ppsf,
 QUANTILE_CONT(price_per_sqft,0.75) AS q75_ppsf
FROM research_sales GROUP BY ALL ORDER BY sales DESC,neighborhood;

CREATE OR REPLACE TABLE quarterly_trends AS
WITH quarterly AS (
 SELECT DATE_TRUNC('quarter',sale_date)::DATE AS quarter,
  building_class_at_time_of_sale, COUNT(*) AS sales,
  MEDIAN(price_per_sqft) AS median_ppsf
 FROM research_sales GROUP BY 1,2
)
SELECT *, LAG(median_ppsf) OVER (PARTITION BY building_class_at_time_of_sale ORDER BY quarter) AS previous_observed_quarter_ppsf,
 (median_ppsf/NULLIF(LAG(median_ppsf) OVER
  (PARTITION BY building_class_at_time_of_sale ORDER BY quarter),0)-1)*100 AS observed_change_pct
FROM quarterly ORDER BY quarter,building_class_at_time_of_sale;

CREATE OR REPLACE TABLE year_class_comparison AS
SELECT YEAR(sale_date) AS sale_year,building_class_at_time_of_sale,
 COUNT(*) AS sales,MEDIAN(price_per_sqft) AS median_ppsf,
 MEDIAN(gross_square_feet) AS median_area
FROM research_sales GROUP BY 1,2 ORDER BY 1,2;
