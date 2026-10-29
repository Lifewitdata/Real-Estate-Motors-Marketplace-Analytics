# Sources and provenance

Provider: NYC Department of Finance. [Annual sales landing page](https://www.nyc.gov/site/finance/property/property-annualized-sales-update.page).

- [2024 Brooklyn workbook](https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/2024/2024_brooklyn.xlsx): 21,994 source rows; 1,161 in C1/C2/C3 scope. Header states PTS data as of April 8, 2025.
- [2025 Brooklyn workbook](https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/2025/2025_brooklyn.xlsx): 23,472 source rows; 1,212 in scope. Header states PTS data as of May 4, 2026.
- [Building class definitions](https://www.nyc.gov/assets/finance/jump/hlpbldgcode.html): C1/C2/C3 interpretation; lookup in config/building_classes.csv.
- [Sales glossary](https://www.nyc.gov/assets/finance/downloads/pdf/07pdf/glossary_rsf071607.pdf): sale price, area, neighborhood and parcel terminology. Zero-price records represent transfers without cash consideration and are not treated as usable price evidence.

Downloaded/verified October 29, 2026. Exact URLs, SHA-256 hashes, row counts and publisher notes are retained in data/sources.json and the generated manifest. These are complementary references from one official provider, not independent verification of sale terms.

The committed CSV is a normalized extract of all 2,373 scoped records, including subsequently excluded records. Source row means the original Excel row number, including workbook headings. Record ID hashes source ID plus row number. Original address/parcel/date/price fields allow a researcher to return to the original source.

Raw workbooks are downloaded by the pipeline and excluded from Git. Snapshot mode verifies the committed extract's SHA-256 and declared row totals before analysis. Full workbook mode normalizes headers, retains row provenance and checks required fields. Annual final-roll property attributes are not necessarily condition at the sale date. Later publication means these records cannot support claims about what was known contemporaneously.
