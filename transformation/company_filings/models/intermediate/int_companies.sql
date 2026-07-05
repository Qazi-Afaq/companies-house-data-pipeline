select
    sp."type",
    sp.company_status,
    sp.company_number,
    sp.company_name,
    sp.date_of_creation,
    sp.accounts_next_due,
    sp.confirmation_statement_next_due,
    sp.sic_codes,
    sp.registered_office_address,
    sp.loaded_at,
    sic_codes_obj->>'code' as sic_code
from {{ ref('stg_profiles') }} sp
cross join lateral (
    select json_array_elements(sp.sic_codes) as sic_codes_obj
) x