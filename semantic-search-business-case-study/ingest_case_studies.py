import os

import boto3
import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pgvector.psycopg2 import register_vector

load_dotenv()

S3_BUCKET = "bucket-nhx-main"
S3_PREFIX = "project-business-case-study/"
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768

genai_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

s3 = boto3.client("s3")
conn = psycopg2.connect(
    host=os.environ["SUPABASE_DB_HOST"],
    port=os.environ["SUPABASE_DB_PORT"],
    dbname=os.environ["SUPABASE_DB_NAME"],
    user=os.environ["SUPABASE_APP_DB_USER"],
    password=os.environ["SUPABASE_APP_DB_PASSWORD"],
)
register_vector(conn)
cur = conn.cursor()

response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
keys = [
    obj["Key"] for obj in response.get("Contents", [])
    if obj["Key"].endswith(".txt")
]

print(f"Found {len(keys)} case study file(s) in S3.")

for key in keys:
    filename = key.split("/")[-1]
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    content = obj["Body"].read().decode("utf-8")

    result = genai_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=content,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    embedding = result.embeddings[0].values

    cur.execute(
        """
        insert into business_case_studies (filename, content, embedding)
        values (%s, %s, %s)
        on conflict (filename) do update
        set content = excluded.content, embedding = excluded.embedding
        """,
        (filename, content, embedding),
    )
    print(f"Ingested: {filename}")

conn.commit()
cur.close()
conn.close()
print("Done.")
