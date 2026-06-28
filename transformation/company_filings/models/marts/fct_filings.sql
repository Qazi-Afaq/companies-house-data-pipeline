{{
    config(
        materialized='incremental',
        unique_key=['company_number', 'end_date']
    )
}}


select *
from {{ ref('stg_filings') }}
{% if is_incremental() %}
    where loaded_at > (select max(loaded_at) from {{ this }})
{% endif %}