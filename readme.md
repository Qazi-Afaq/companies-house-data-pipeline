This project is a data pipeline that extracts data from the public register of UK's companies house, covering annual-filings, company-profiles and persons-with-significant-control. This data is transformed using DBT for business ready analytics.

The pipeline supports:

- **Financial performance** — profitability, liquidity, and year-over-year growth trends per company
- **Industry benchmarking** — ranking companies by operating margin within their SIC code and filing year
- **Ownership & control analysis** — PSC nature-of-control breakdowns and demographic distribution
- **Company reference data** — profiles, incorporation details, and SIC classifications

ARCHITECTURE:
This is an ELT pipeline. The company data(json files) is fetched from the companies-house API into an S3 bucket. 
Each pipeline execution fetches the json files from the S3 bucket using python script running on EC2 instance.
The python script flattens and cleans the data, ready to be loaded into the data warehouse.
DBT is then used to transform the data into business-ready analytics.
The pipeline is triggered by airflow.
Each JSON file represents one company data including all it's financial years filings, it's associated company profiles and psc.

Companies House API
        │
        ▼
   Raw JSON (S3)
        │
        ▼
Python/pandas ingestion  ──►  src_ tables (PostgreSQL)
        │
        ▼
   dbt staging (stg_)      — 1:1 with source, light typing/cleaning
        │
        ▼
   dbt intermediate (int_) — business logic, joins, enrichment
        │
        ▼
   dbt marts (fct_/dim_)   — analytics-ready, consumption layer
        │
        ▼
   Orchestrated by Airflow (WSL2)

   ![image alt](https://github.com/Qazi-Afaq/companies-house-data-pipeline/blob/main/docs/images/dbt-dag%20(1).png?raw=true)
   
   ![image alt](https://github.com/Qazi-Afaq/companies-house-data-pipeline/blob/main/docs/images/run_dbt_models-graph.png?raw=true)

   

