


select *
from "postgres"."finance_companies"."stg_filings"

    where loaded_at > (select max(loaded_at) from "postgres"."finance_companies"."mart_filings")
