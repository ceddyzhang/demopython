import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(
    host=os.environ["SUPABASE_DB_HOST"],
    port=6543,
    dbname=os.environ["SUPABASE_DB_NAME"],
    user=os.environ["SUPABASE_DB_USER"],
    password=os.environ["SUPABASE_DB_PASSWORD"],
)
cur = conn.cursor()
cur.execute("select 1")
print("Connected via transaction pooler (port 6543):", cur.fetchone())
cur.close()
conn.close()
