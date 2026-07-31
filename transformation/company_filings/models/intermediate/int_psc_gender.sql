

select "name" , forename , 
title , company_number,
(case
	when title = 'ms' then 'f'
	when title = 'mr' then 'm'
	else predicted_gender
end) as predicted_gender
from {{ref('stg_psc')}} psc
left join {{ref('name_gender_dataset_processed')}} ng
on psc.forename  = ng."name"