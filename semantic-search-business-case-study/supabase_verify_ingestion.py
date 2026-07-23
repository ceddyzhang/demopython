import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(
    host=os.environ["SUPABASE_DB_HOST"],
    port=os.environ["SUPABASE_DB_PORT"],
    dbname=os.environ["SUPABASE_DB_NAME"],
    user=os.environ["SUPABASE_APP_DB_USER"],
    password=os.environ["SUPABASE_APP_DB_PASSWORD"],
)
cur = conn.cursor()
cur.execute("select filename, length(content), vector_dims(embedding) from business_case_studies order by filename")
for row in cur.fetchall():
    print(row)
cur.close()
conn.close()
