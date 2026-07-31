with deduped as (
    select *,
        row_number() over (partition by company_number order by loaded_at desc) as rn
    from {{ source('src_tables', 'src_psc') }}
)

select 
    lower(forename::varchar(255))              as forename,
    lower(surname::varchar(255))                as surname,
    lower(title::varchar(255))                  as title,
    result_number::integer                      as result_number,
    date_of_birth_month::integer                as date_of_birth_month,
    date_of_birth_year::integer                 as date_of_birth_year,
    lower(nationality::varchar(255))            as nationality,
    lower(country_of_residence::varchar(255))   as country_of_residence,
    {{ target.schema }}.cast_to_date(notified_on) as notified_on,
    lower(address_address_line_1::text)         as address_address_line_1,
    lower(address_address_line_2::text)         as address_address_line_2,
    lower(address_country::text)                as address_country,
    lower(address_locality::text)               as address_locality,
    lower(postal_code::text)                    as postal_code,
    natures_of_control::json                    as natures_of_control,
    company_number::varchar(255)                as company_number,
    loaded_at::timestamptz                      as loaded_at
from deduped 
where rn = 1