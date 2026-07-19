# USGS Earthquake Data Pipeline

An end-to-end data engineering pipeline that ingests real-time earthquake data from the USGS API, processes it with PySpark, and writes structured output to a data lake on AWS S3.

## Architecture

```
USGS API → AWS Lambda (ingest) → S3 (raw JSON) → PySpark (transform) → S3 (Parquet)
```

| Layer | Tool | Description |
|---|---|---|
| Ingestion | AWS Lambda + Python | Fetches live earthquake feed, flattens GeoJSON, writes one record per earthquake |
| Raw Storage | AWS S3 | Partitioned by `year/month/day` for efficient querying |
| Transformation | PySpark (local) | Reads raw JSON, applies transformations, computes aggregations |
| Curated Storage | AWS S3 | Writes Parquet output to a curated layer |

## Project Structure

```
spark-test/
├── spark_earthquake_process_s3.py   # PySpark transformation job
└── lambda_ingest/
    └── lambda_function.py           # AWS Lambda ingestion handler
```

## What the Pipeline Does

**Ingestion (Lambda)**
- Calls the [USGS Earthquake Feed API](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) on demand
- Flattens the nested GeoJSON structure (properties + geometry coordinates)
- Enriches each record with `ingestion_time` and partitions by event date
- Writes one JSON file per earthquake to S3: `project-usgs/staging/year=YYYY/month=MM/day=DD/{earthquake_id}.json`

**Transformation (PySpark)**
- Reads all raw JSON files from S3 using the Hadoop AWS connector
- Identifies the 2 most recent earthquakes by `event_time`
- Computes the maximum magnitude across those records
- Writes aggregated result to S3 as Parquet: `project-usgs/curated/`

## Tech Stack

- **PySpark** — DataFrame API, aggregations, S3 I/O via `hadoop-aws`
- **AWS Lambda** — serverless ingestion, triggered on demand
- **AWS S3** — raw (JSON) and curated (Parquet) storage layers
- **Python** — `boto3`, `configparser`, `urllib`

## Local Setup

**Prerequisites**
- WSL (Ubuntu 22.04)
- Python 3.x
- Java 11+
- AWS credentials configured at `~/.aws/credentials`

**Install dependencies**
```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install pyspark boto3
```

**Run the pipeline**
```bash
source .venv-wsl/bin/activate
python3 spark-test/spark_earthquake_process_s3.py
```

## S3 Output Structure

```
bucket-nhx-main/
├── project-usgs/
│   ├── staging/
│   │   └── year=2026/month=04/day=13/
│   │       ├── us7000n1ab.json
│   │       └── nc75321047.json
│   └── curated/
│       └── avg_magnitude/
│           ├── part-00000-*.snappy.parquet
│           └── _SUCCESS
```

## Design Decisions

- **Local Spark, cloud storage** — Spark runs locally on WSL to keep costs at zero. S3 handles durable storage. This is a deliberate tradeoff appropriate for a low-volume demo pipeline.
- **Parquet output** — columnar format enables efficient downstream querying via AWS Athena without additional processing.
- **Credentials via file reference** — AWS keys are read from the local credentials file at runtime. No secrets are hardcoded or committed to git.
- **Partitioned raw layer** — Lambda writes data partitioned by date, enabling partition pruning if the dataset grows.

## Future Improvements

- Schedule Lambda via EventBridge to run hourly
- Add a window function layer: rank earthquakes by magnitude within each day
- Query curated Parquet layer via AWS Athena
- Orchestrate the full pipeline with Apache Airflow
