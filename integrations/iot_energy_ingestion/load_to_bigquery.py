from __future__ import annotations

import argparse
from pathlib import Path

from google.cloud import bigquery, storage

try:
    from .config import get_settings
except ImportError:
    from config import get_settings


def ensure_resources(client: bigquery.Client, dataset_id: str) -> None:
    dataset_ref = bigquery.Dataset(f"{client.project}.{dataset_id}")
    dataset_ref.location = get_settings().region
    client.create_dataset(dataset_ref, exists_ok=True)


def upload_to_gcs(file_path: Path, bucket_name: str, object_name: str) -> str:
    storage_client = storage.Client(project=get_settings().project_id)
    bucket = storage_client.bucket(bucket_name)
    if not bucket.exists():
        bucket = storage_client.create_bucket(bucket_name, location=get_settings().region)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(file_path)
    return f"gs://{bucket_name}/{object_name}"


def load_jsonl_to_bigquery(gcs_uri: str, table_id: str) -> None:
    client = bigquery.Client(project=get_settings().project_id)
    ensure_resources(client, get_settings().raw_dataset)

    schema = [
        bigquery.SchemaField("ingestion_batch_id", "STRING"),
        bigquery.SchemaField("event_id", "STRING"),
        bigquery.SchemaField("device_id", "STRING"),
        bigquery.SchemaField("building_id", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("energy_consumption", "FLOAT"),
        bigquery.SchemaField("temperature", "FLOAT"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("ingested_at", "TIMESTAMP"),
        bigquery.SchemaField("source_file", "STRING"),
    ]

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="timestamp",
        ),
        clustering_fields=["building_id", "device_id", "status"],
    )

    load_job = client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
    load_job.result()
    print(f"Loaded {gcs_uri} into {table_id}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a JSONL file to GCS and load it into BigQuery.")
    parser.add_argument("--file-path", required=True, help="Local JSONL file path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    file_path = Path(args.file_path)
    settings = get_settings()
    batch_id = file_path.stem.removeprefix("iot_energy_")
    year = batch_id[0:4]
    month = batch_id[4:6]
    object_name = f"iot_energy/year={year}/month={month}/{file_path.name}"
    gcs_uri = upload_to_gcs(file_path, settings.raw_bucket, object_name)
    table_id = f"{settings.project_id}.{settings.raw_dataset}.iot_energy_events_raw"
    load_jsonl_to_bigquery(gcs_uri, table_id)


if __name__ == "__main__":
    main()
