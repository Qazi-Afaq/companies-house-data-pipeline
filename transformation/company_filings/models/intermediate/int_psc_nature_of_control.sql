select forename, surname, natures_of_control, extracted_nature_of_control
category,band_low,band_high
from {{ref('stg_psc')}} sp
cross join lateral (
	select json_array_elements_text(sp.natures_of_control) as extracted_nature_of_control
) x
left join {{ref('nature_of_control')}} noc
on x.extracted_nature_of_control = noc.nature_of_control
order by forename