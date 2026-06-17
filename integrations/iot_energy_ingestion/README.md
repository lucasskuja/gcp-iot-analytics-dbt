# IoT Energy Ingestion

Batch ingestion service for the IoT energy platform, designed to run as a Cloud Run Job.

## Responsibilities

- generate synthetic IoT telemetry for smart-building energy monitoring
- inject realistic upstream data quality issues
- persist raw JSONL files to GCS for replay and auditability
- append raw events into the BigQuery landing layer

## Why this service exists

The ingestion step is intentionally isolated from orchestration and analytical transformation. This keeps the runtime boundary clear:

- Cloud Run handles batch execution and container lifecycle
- Composer orchestrates the job and downstream dependencies
- dbt owns analytical transformation after the raw load is complete

## Execution

```bash
python run_ingestion.py --execution-date 2026-04-26T10:00:00 --intervals 96 --output-dir /tmp/iot-energy-data
```

## Operational notes

- the service generates batch-scoped files and records for deterministic daily runs
- the raw landing layer supports replay and troubleshooting
- test coverage focuses on ingestion orchestration and event generation behavior
