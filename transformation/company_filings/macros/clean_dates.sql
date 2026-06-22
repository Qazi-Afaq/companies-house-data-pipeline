create or replace function cast_to_date(date_value) returns DATE language plpgsql as
$$
begin
    return date_value::date
EXCEPTION
    when others then
        return NULL
end;
$$;