create or replace function list_tables_in_schema(schema_name text default 'public')
returns table(table_name text)
language sql
as $$
    select tablename
    from pg_tables
    where schemaname = schema_name;
$$;

-- Allow all users to read all rows (for testing)
create policy "Allow read access to all"
on users
for select
using (true);

-- Disable RLS, not with the above query
