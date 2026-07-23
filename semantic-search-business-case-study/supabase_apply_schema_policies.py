import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()
conn = psycopg2.connect(
    host=os.environ["SUPABASE_DB_HOST"],
    port=os.environ["SUPABASE_DB_PORT"],
    dbname=os.environ["SUPABASE_DB_NAME"],
    user=os.environ["SUPABASE_DB_USER"],
    password=os.environ["SUPABASE_DB_PASSWORD"],
)
conn.autocommit = True
cur = conn.cursor()

# Schema-level: any FUTURE table in public auto-grants these, no per-table GRANT needed.
cur.execute("alter default privileges in schema public grant select on tables to anon, authenticated;")
cur.execute(
    "alter default privileges in schema public grant select, insert, update, delete "
    "on tables to business_case_study_app;"
)
print("Default privileges set for future tables in public schema.")

# Per-table (current tables only — RLS has no schema-wide switch): enable RLS +
# apply the same two standard policies to every table in public. Idempotent —
# safe to rerun whenever a new table is added.
cur.execute("""
    select tablename from pg_tables where schemaname = 'public'
""")
tables = [row[0] for row in cur.fetchall()]
print(f"Applying standard RLS policies to {len(tables)} table(s): {tables}")

for table in tables:
    cur.execute(
        sql.SQL("alter table public.{} enable row level security").format(sql.Identifier(table))
    )

    read_policy = f"{table}_public_read"
    cur.execute("select 1 from pg_policies where tablename = %s and policyname = %s", (table, read_policy))
    if not cur.fetchone():
        cur.execute(
            sql.SQL("create policy {} on public.{} for select to anon, authenticated using (true)")
            .format(sql.Identifier(read_policy), sql.Identifier(table))
        )
        print(f"  {table}: created read-only policy for anon/authenticated")

    app_policy = f"{table}_app_full_access"
    cur.execute("select 1 from pg_policies where tablename = %s and policyname = %s", (table, app_policy))
    if not cur.fetchone():
        cur.execute(
            sql.SQL(
                "create policy {} on public.{} for all to business_case_study_app "
                "using (true) with check (true)"
            ).format(sql.Identifier(app_policy), sql.Identifier(table))
        )
        print(f"  {table}: created full-access policy for business_case_study_app")

cur.close()
conn.close()
print("Done.")
