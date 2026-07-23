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
conn.autocommit = True
cur = conn.cursor()

cur.execute("create extension if not exists vector;")
cur.execute("""
    create table if not exists business_case_studies (
        id bigserial primary key,
        filename text not null unique,
        content text not null,
        embedding vector(768),
        created_at timestamptz default now()
    );
""")
cur.execute("""
    create index if not exists business_case_studies_embedding_idx
    on business_case_studies using hnsw (embedding vector_cosine_ops);
""")

cur.execute("select table_name from information_schema.tables where table_schema = %s", ("public",))
print("Tables in public schema now:", [r[0] for r in cur.fetchall()])

cur.close()
conn.close()
