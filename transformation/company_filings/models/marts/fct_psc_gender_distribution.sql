with calculated as (
    select
        company_number,
        count(*) as total_people,
        count(case when predicted_gender = 'm' then 1 end) as total_males,
        count(case when predicted_gender = 'f' then 1 end) as total_females
    from {{ ref('int_psc_gender') }}
    group by company_number
)
select
    total_people,
    company_number,
    round((total_males::numeric / nullif(total_people, 0)) * 100, 2) as male_percentage,
    round((total_females::numeric / nullif(total_people, 0)) * 100, 2) as female_percentage
from calculated