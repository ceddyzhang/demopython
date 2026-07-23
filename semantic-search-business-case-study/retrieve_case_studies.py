import os
import sys

import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pgvector.psycopg2 import register_vector

load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768
TOP_K = 4


def get_genai_client():
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def get_connection():
    conn = psycopg2.connect(
        host=os.environ["SUPABASE_DB_HOST"],
        port=os.environ["SUPABASE_DB_PORT"],
        dbname=os.environ["SUPABASE_DB_NAME"],
        user=os.environ["SUPABASE_APP_DB_USER"],
        password=os.environ["SUPABASE_APP_DB_PASSWORD"],
    )
    register_vector(conn)
    return conn


def retrieve(query: str, conn, genai_client, top_k: int = TOP_K):
    result = genai_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    query_embedding = result.embeddings[0].values

    cur = conn.cursor()
    cur.execute(
        """
        select filename, content, embedding <=> %s::vector as distance
        from business_case_studies
        order by distance
        limit %s
        """,
        (query_embedding, top_k),
    )
    rows = cur.fetchall()
    cur.close()
    return rows


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or (
        "a company relied too heavily on what made it successful in the past and was "
        "slow to respond when a cheaper, more convenient alternative won over customers"
    )
    conn = get_connection()
    genai_client = get_genai_client()

    print(f"Query: {query}\n")
    for filename, content, distance in retrieve(query, conn, genai_client):
        snippet = content[:100].replace("\n", " ")
        print(f"{distance:.4f}  {filename}")
        print(f"        {snippet}...\n")

    conn.close()
