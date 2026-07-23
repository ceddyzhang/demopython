import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(
    host=os.environ["SUPABASE_DB_HOST"],
    port=os.environ["SUPABASE_DB_PORT"],
    dbname=os.environ["SUPABASE_DB_NAME"],
    user=os.environ["SUPABASE_DB_USER"],
    password=os.environ["SUPABASE_DB_PASSWORD"],
)
cur = conn.cursor()

cur.execute("""
    select rolname, rolbypassrls, rolsuper
    from pg_roles
    where rolname in ('anon', 'authenticated', 'service_role', 'business_case_study_app', 'postgres')
    order by rolname
""")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
