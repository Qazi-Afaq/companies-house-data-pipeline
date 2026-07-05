with deduped as (
    select *,
        row_number() over (
            partition by company_number
            order by loaded_at desc
        ) as rn
    from {{ source('src_tables', 'src_profiles') }}
)

select
    d."type"::text,
    company_status::varchar(255),
    company_number::varchar(255),
    company_name::varchar(255),
    {{ target.schema }}.cast_to_date(date_of_creation) as date_of_creation,
    {{ target.schema }}.cast_to_date(accounts_next_due) as accounts_next_due,
    {{ target.schema }}.cast_to_date(confirmation_statement_next_due) as confirmation_statement_next_due,
    sic_codes::json,
    registered_office_address::json,
    loaded_at::timestamptz
from deduped d
where rn = 1