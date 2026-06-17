# Integrations

This directory contains integration workloads that run outside Cloud Composer, typically as containerized batch jobs deployed to Cloud Run Jobs.

The goal of this structure is to keep ingestion and external-system interaction logic isolated from orchestration and analytical modeling. Each integration can evolve with its own runtime dependencies, release cadence, and CI/CD path.

## Design principles

- one subdirectory per deployable integration
- each integration owns its application code, dependency manifest, container image definition, and tests
- deployment pipelines can be triggered selectively by repository path
- operational concerns stay close to the integration that owns them

## Current integration

- `iot_energy_ingestion/`
  Batch ingestion job that generates synthetic IoT telemetry, persists raw files to GCS, and appends data into the BigQuery raw layer.

## Why this matters

This layout reflects a production-minded repository structure. As the platform grows, it becomes easier to add new ingestion jobs without coupling all integrations to a single shared runtime or release process.
