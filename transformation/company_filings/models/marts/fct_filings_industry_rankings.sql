select 
    ff.company_number,
    company_name,
    ff.end_date,
    ff.end_date_year,
    ic.sic_code,
    ff.operating_margin,
    case 
        when ff.operating_margin is null then null
        else dense_rank() over (
            partition by ic.sic_code, ff.end_date_year 
            order by ff.operating_margin desc nulls last
        )
    end as operating_margin_rank
from {{ ref('fct_filings_enriched') }} ff 
left join {{ ref('int_companies') }} ic
    on ff.company_number = ic.company_number