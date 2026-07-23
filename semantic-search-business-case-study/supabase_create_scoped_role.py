import os
import secrets
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

ROLE_NAME = "business_case_study_app"
new_password = secrets.token_urlsafe(24)

conn = psycopg2.connect(
    host=os.environ["SUPABASE_DB_HOST"],
    port=os.environ["SUPABASE_DB_PORT"],
    dbname=os.environ["SUPABASE_DB_NAME"],
    user=os.environ["SUPABASE_DB_USER"],
    password=os.environ["SUPABASE_DB_PASSWORD"],
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("select 1 from pg_roles where rolname = %s", (ROLE_NAME,))
if cur.fetchone():
    cur.execute(
        sql.SQL("alter role {} with password %s").format(sql.Identifier(ROLE_NAME)),
        (new_password,),
    )
    print(f"Role {ROLE_NAME} already existed — password rotated.")
else:
    cur.execute(
        sql.SQL("create role {} with login password %s").format(sql.Identifier(ROLE_NAME)),
        (new_password,),
    )
    print(f"Role {ROLE_NAME} created.")

cur.execute(sql.SQL("grant connect on database {} to {}").format(
    sql.Identifier(os.environ["SUPABASE_DB_NAME"]), sql.Identifier(ROLE_NAME)))
cur.execute(sql.SQL("grant usage on schema public to {}").format(sql.Identifier(ROLE_NAME)))
cur.execute(sql.SQL("grant select, insert, update on business_case_studies to {}").format(sql.Identifier(ROLE_NAME)))
cur.execute(sql.SQL("grant usage, select on sequence business_case_studies_id_seq to {}").format(sql.Identifier(ROLE_NAME)))

cur.close()
conn.close()

env_path = ".env"
with open(env_path, "r") as f:
    lines = [l for l in f.readlines() if not l.startswith("SUPABASE_APP_DB_")]
if lines and not lines[-1].endswith("\n"):
    lines[-1] += "\n"

project_ref = os.environ["SUPABASE_DB_USER"].split(".")[-1]
lines.append(f"SUPABASE_APP_DB_USER={ROLE_NAME}.{project_ref}\n")
lines.append(f"SUPABASE_APP_DB_PASSWORD={new_password}\n")

with open(env_path, "w") as f:
    f.writelines(lines)

print("Scoped role credentials written to .env as SUPABASE_APP_DB_USER / SUPABASE_APP_DB_PASSWORD.")
print("(Password not printed to console.)")
