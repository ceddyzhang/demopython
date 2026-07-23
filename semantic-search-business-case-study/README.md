# Semantic Search: Business Case Study Finder

Natural-language search over a library of business case studies, so a query about a current situation surfaces analogous past cases even when the wording shares no keywords (e.g., a "surprise pest discovery" case and a "surprise flood discovery" case are the same underlying pattern — an office crisis discovered unexpectedly — but keyword search would never connect them).

## Persona & pain point

**Who:** an analyst/consultant trying to answer "have we seen a situation like this before?"

**Why keyword search fails:** case studies are narrative prose, and the same underlying business pattern gets described with completely different vocabulary across cases (different decades, industries, authors). Exact-term search misses the analogy entirely.

**What "good" looks like:** given a query describing a current situation, return past case studies with the same underlying pattern, ranked by relevance — and correctly exclude cases that are unrelated, even if they share surface words.

## Architecture

```
[S3: case study .txt files] → [Data pipeline] → [Embedding API] → [Vector DB]
                                                                        ↑
                                                  [User query] → [Embedding API]
                                                                        ↓
                                                          [Retrieval / ranking logic]
                                                                        ↓
                                                            [Streamlit frontend]
```

## Components

| Component | Role | Choice |
|---|---|---|
| **Raw data storage** | One .txt file per case study, source of truth for ingestion. | S3 (`s3://bucket-nhx-main/project-business-case-study/`) |
| **Data pipeline** | Reads each .txt file from S3, embeds it (whole-document — cases are short), writes vector + metadata to the DB. Handles incremental adds (re-embed only new/changed files). | Python script |
| **Embedding API** | Converts case text → vector. Bought, not built. | Google Gemini embedding API (free tier), model `gemini-embedding-001`, truncated to 768 dims via `output_dimensionality` (default is 3072; 768 is one of Google's recommended reduced sizes and matches our table schema) |
| **Vector DB** | Stores vectors + metadata; provides nearest-neighbor search primitive. Hosted so the demo works independent of any local machine. | pgvector on Supabase (free tier) |
| **Retrieval/ranking logic** | Top-k similarity search, no strict metadata filtering needed (exploratory use case, not precision-critical like legal precedent search) — optional keyword-vs-semantic comparison to prove the value prop. | Python |
| **Frontend** | Search box + ranked results with matched snippet and similarity score; side-by-side keyword vs. semantic comparison. Deployed, not just local, so it's shareable as a live link. | Streamlit, deployed on Streamlit Community Cloud (free) |

All three pieces are hosted, not local — the demo works as a shareable link independent of any machine being on. Every choice is free-tier; no self-hosted component, keeping the "embedding/vector search infra is bought, pipeline and retrieval logic are built" story intact.

## Why this isn't "legal case search"

Same document genre (narrative "case studies"), different system design: legal precedent search must be precision/recall-critical (a missed or wrong citation is a real liability), needs jurisdiction/binding-authority metadata, and favors hybrid exact-citation + doctrinal matching. This use case is exploratory/inspirational — a loosely-relevant result is still useful, so pure semantic top-k similarity is sufficient. Same underlying tech, deliberately different retrieval design.

## Scope

- **V1 (this POC):** semantic search only — retrieval, no generation.
- **V2 (stretch):** add an LLM generation step on top of retrieved results → becomes RAG (e.g., "here's why this past case is analogous").

## Test dataset

Real short-form business case studies, one file = one case, stored in S3 at `s3://bucket-nhx-main/project-business-case-study/`:

- `blockbucster-vs-netflix-2000.txt` — incumbent protects a profitable legacy model, dismisses a disruptive shift, goes bankrupt while the challenger thrives.
- `kodak-and-fuji-2012.txt` — same underlying pattern as above (industry-wide disruption; one player declines, one repositions), different vocabulary/industry.
- `swatch-quartz-1970s.txt` — same pattern again, deliberately written to avoid words shared with the other two ("bankruptcy," "disruption," "digital"), to test whether retrieval finds the analogy on meaning alone.
- `lego-business-in-2000s.txt` — a contrasting pattern: internal loss of focus/over-expansion, successfully self-corrected — not an "ignored external disruption" story.

The first three should cluster together under a semantic query even though they share almost no literal vocabulary; LEGO should rank lower since it's a genuinely different underlying pattern. See conversation history for the deeper discussion of why "same genre" (business case study) isn't the same thing as "same pattern," and why outcome (success vs. failure) is itself part of what an embedding model treats as meaning, not a separable dimension.

## Database provisioning

One-time/occasional setup scripts (run locally, not part of the live app):

| Script | Purpose |
|---|---|
| `supabase_setup_schema.py` | Enables the `vector` extension, creates the `business_case_studies` table, creates the HNSW similarity index. |
| `supabase_create_scoped_role.py` | Creates the `business_case_study_app` role for the app to use day-to-day instead of the superuser. Generates its password and writes it directly to `.env`, never printed to any log. Grants SELECT/INSERT/UPDATE/**DELETE** (DELETE kept deliberately, unlike typical least-privilege defaults, so the table can be wiped and reloaded during development). |
| `supabase_apply_schema_policies.py` | Enables RLS and applies two standard policies to every table in `public` (see RLS section below); also sets `ALTER DEFAULT PRIVILEGES` so future tables auto-grant the right base privileges. Idempotent — safe to rerun after adding a new table. |
| `supabase_check_rls.py` | Diagnostic: prints `rolbypassrls`/`rolsuper` for the key roles, to confirm which roles RLS actually restricts. |
| `supabase_test_pooler_connection.py` | Diagnostic: tests connectivity via the transaction pooler (port 6543) in isolation — useful if pooler-specific connection issues recur. |

**Credentials:** copy `.env.example` to `.env` and fill in real values — `.env` is gitignored, never commit it. Connection params are stored as discrete fields (`SUPABASE_DB_HOST`/`PORT`/`NAME`/`USER`/`PASSWORD`), not a single URI — a password containing special characters (e.g. `@`) breaks URI parsing since `@` is also the credentials/host delimiter, so discrete fields sidestep that entirely.

**Gotcha #1 — IPv6-only direct connections:** Supabase's direct connection hostname (`db.<ref>.supabase.co`) resolves to IPv6 only. On a network without IPv6 connectivity, this fails at DNS resolution with a confusing error. Fix: use a pooler connection instead (IPv4-compatible).

**Gotcha #2 — Session pooler outage:** the Session pooler (port 5432) can fail with `server closed the connection unexpectedly` while the underlying database is completely healthy (confirmed via Postgres logs showing normal query activity) — this was a pooler-component-specific issue, not a database or credentials problem. Fix: use the **Transaction pooler (port 6543)** instead — same host, different port. This project uses port 6543 for that reason.

**Gotcha #3 — Pooler username format:** the connection pooler requires the project ref appended to any role's username (`business_case_study_app.<project-ref>`, not just `business_case_study_app`) to route correctly — omitting it fails with a `no tenant identifier provided` error, not an auth error, which is a useful signal for diagnosing this specific issue versus a wrong password.

**Provisioning workflow used:** create the role → verify it's the only one matching (no stray/duplicate roles) → only then remove the verification script. Any script that programmatically edits `.env` (like the role-creation script) must ensure the file ends in a newline before appending — otherwise a new line silently merges onto the end of the previous value, corrupting it without an obvious error until the next connection attempt fails.

## Row Level Security

Supabase grants `anon`/`authenticated` full SELECT/INSERT/UPDATE/DELETE/TRUNCATE on every `public` table **by default** — this is deliberate on Supabase's part (RLS is meant to be the actual gate; GRANT is just the ceiling of what's possible), not a bug, but it means a freshly created table is fully publicly writable via the auto-generated REST API until RLS is enabled. Verified this concretely via `information_schema.role_table_grants` before treating it as fact.

Current policy (applied to every table in `public` via `supabase_apply_schema_policies.py`):
- **`anon`/`authenticated`**: read-only (`for select ... using (true)`) — intentional, so the Streamlit demo's results are viewable without authentication.
- **`business_case_study_app`**: full access (`for all ... using (true) with check (true)`) — matches the GRANTs it already has.

Since RLS is per-table in Postgres (no native schema-wide switch), `supabase_apply_schema_policies.py` is the schema-level control mechanism here: rerun it after adding any new table to apply the same two policies automatically.

## Ingestion pipeline

| Script | Purpose |
|---|---|
| `ingest_case_studies.py` | Reads all `.txt` files from the S3 prefix, embeds each with Gemini, upserts (by `filename`) into `business_case_studies`. Runs locally/on-demand — not part of the deployed app. Connects using the scoped `business_case_study_app` role, not the superuser. |
| `supabase_verify_ingestion.py` | Sanity check: prints filename, content length, and embedding dimensionality for every row — rerun after any ingestion to confirm it landed correctly. |

**SDK note:** `google-generativeai` is fully deprecated (no more updates/fixes) — this project uses the current `google-genai` SDK (`from google import genai`) instead. The embedding call also needed a live check of available models (`gemini-embedding-001`, not the older `text-embedding-004`, which no longer exists) rather than assuming a remembered model name still works — API surfaces for fast-moving AI products change often enough that verifying beats assuming.

**Naming convention:** scripts that operate on/verify Supabase are prefixed `supabase_*` for consistency; `test_` was deliberately avoided as a prefix even for diagnostic scripts, since `pytest` auto-discovers `test_*.py` files and these aren't pytest-style tests (no assertions, hit live infrastructure) — that prefix would be misleading, not just stylistic.

## Retrieval logic

`retrieve_case_studies.py`: embeds the query with the same model/config used for ingestion (must match — mixing embedding spaces produces meaningless distances), then runs a single SQL query using pgvector's cosine distance operator (`<=>`) to rank all rows by similarity:

```sql
select filename, content, embedding <=> %s::vector as distance
from business_case_studies
order by distance
limit %s
```

**Distance metric:** cosine distance (`<=>`), not Euclidean (`<->`) or dot product (`<#>`) — matches the HNSW index, which was built with `vector_cosine_ops` (using a different operator than the index type means Postgres can't use the index, forcing a full scan). Cosine is also the standard choice for text embeddings generally: embedding models optimize for the *direction* of the vector as the carrier of meaning, not magnitude, so cosine (which ignores magnitude) is the metric that matches how these models were actually trained.

**Cast gotcha — array→`vector` is an assignment-only cast, not implicit:** Postgres casts come in three tiers — implicit (applied automatically almost anywhere), assignment (applied automatically only in `INSERT`/`UPDATE`/function-return contexts), and explicit (`value::type`, never automatic). pgvector's array→`vector` conversion is assignment-tier, which is why `ingest_case_studies.py`'s `INSERT ... VALUES (%s)` worked with a raw Python list with no cast (INSERT is an assignment context), but `embedding <=> %s` failed with `operator does not exist: vector <=> numeric[]` (a general expression isn't an assignment context, so Postgres won't auto-cast there). Fix: `%s::vector` — an explicit cast, always honored. This is a general Postgres behavior, not pgvector-specific, and applies to any custom/extension type.

**Validated result:** a query designed to share zero literal vocabulary with any stored case study ("a company relied too heavily on what made it successful in the past and was slow to respond when a cheaper, more convenient alternative won over customers") correctly ranked Swatch/Blockbuster/Kodak (the shared-pattern cluster) above LEGO (the contrasting pattern) — confirming semantic retrieval works as designed, not just that the pipeline runs.
