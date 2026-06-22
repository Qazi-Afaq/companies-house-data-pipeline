
    create or replace function finance_companies.cast_to_date(p_date TEXT) returns date language plpgsql as 
    $$
    begin
        return p_date::date;
    exception
        when others then
            return NULL;
    end;
    $$;
