# Data Platform Architecture

## Objective

This platform simulates a modern GCP-based data environment for monitoring energy consumption from IoT devices in smart buildings. The goal is to showcase architecture decisions, technical trade-offs, cloud cost awareness, and a deployment model that is closer to how production data platforms are actually structured.

## Repository operating model

The repository is intentionally organized to separate source code from deployment artifacts:

- `integrations/`: containerized Python workloads for ingestion jobs
- `composer/`: content synchronized to the Cloud Composer bucket
- `infra/terraform/`: GCP infrastructure as code
- `docs/`: architecture and design documentation

Inside `composer/`, the structure follows the same layout expected by the Composer bucket:

- `composer/dags/`
- `composer/plugins/`
- `composer/data/`

The dbt project lives in `composer/dags/gcp_iot_analytics_dbt/dbt_project/` so the DAG can execute `dbt-bigquery` directly in the Composer runtime without requiring an external repository checkout.

Inside `integrations/`, each directory represents an independently deployable unit. This mirrors a more realistic platform setup in which multiple ingestion jobs may have their own runtime dependencies and release cycles.

## Adopted production-style flow

1. `Cloud Composer` schedules and orchestrates the pipeline.
2. The DAG triggers a batch `Cloud Run Job`, currently packaged under `integrations/iot_energy_ingestion/`.
3. The job generates synthetic IoT telemetry, writes the raw file to `GCS`, and loads the raw data into `BigQuery`.
4. The DAG runs `dbt deps`, `dbt run`, `dbt snapshot`, and `dbt test` using the dbt project synchronized to the Composer bucket.
5. The pipeline finishes with logs, basic metrics, and mocked alerts.

## Why each technology was chosen

### Cloud Run Jobs

Cloud Run Jobs was chosen for ingestion because the workload is finite and batch-oriented. That makes Jobs a stronger fit than an always-on HTTP service.

Advantages:

- serverless execution model
- well-suited for scheduled batch workloads
- straightforward scaling model
- clean separation for ingestion runtime ownership

Trade-offs:

- requires image build and versioning workflows
- debugging and observability depend heavily on GCP logs
- as the number of integrations grows, image ownership and release discipline become more important

### One integration folder per job

The repository uses one folder per integration to support path-based CI/CD and runtime separation.

Advantages:

- each job can keep its own Dockerfile and dependency stack
- CI/CD can deploy only what changed
- ownership and maintenance boundaries are clearer

Trade-offs:

- some structural repetition across integrations
- requires standards to avoid excessive divergence between jobs

### Cloud Composer

Composer was chosen because the platform needs explicit coordination between ingestion, transformation, and testing steps.

Advantages:

- Airflow is widely recognized in enterprise data teams
- retries, dependencies, sensors, and execution logs are mature
- strong integration with GCP-native operators

Trade-offs:

- significant fixed cost
- heavier operational footprint than fully serverless schedulers
- requires disciplined synchronization of bucket-based deployment artifacts

### BigQuery

BigQuery remains the warehouse and analytical execution layer.

Advantages:

- runs dbt models directly
- integrates well with GCS
- strong performance for analytics workloads
- low operational overhead compared with self-managed engines

Trade-offs:

- query cost depends heavily on modeling discipline and filter strategy
- incremental logic, partitioning, and clustering need to be applied intentionally

### dbt-bigquery

`dbt-bigquery` was selected to structure analytics transformation, testing, snapshots, and documentation in a maintainable way.

Advantages:

- supports a layered analytics model design
- improves traceability of transformation logic
- makes testing and documentation part of the development workflow

Trade-offs:

- depends on a runtime where dbt is installed and versioned correctly
- because it is embedded in the Composer artifact, deployment versioning must stay disciplined

### GCS

GCS keeps the raw layer inexpensive, auditable, and replayable.

Trade-offs:

- adds another stage between generation and analytics consumption
- requires retention and path conventions to stay manageable over time

## Key trade-offs in the Composer layout

### Why dbt is placed inside `composer/dags`

Rationale:

- the DAG and dbt project stay co-located
- the Composer bucket becomes a self-contained execution artifact
- CI/CD can synchronize orchestration assets from a single directory root

Trade-off:

- increases the size of the synchronized artifact
- requires discipline so the Composer bucket is not treated as the primary development surface

### Why path-based sync CI is preserved

Rationale:

- reduces unnecessary deployments
- separates orchestration changes from infrastructure changes

Trade-off:

- requires a clear convention for where each class of asset belongs in the repository

## Data quality and observability

The platform intentionally simulates common upstream issues:

- duplicate events
- null measurements
- negative energy values
- delayed events
- unstable device status

Included controls:

- `not null`, `unique`, and `accepted_values` tests
- custom freshness and null-threshold checks
- `dbt` CI with dependency validation, parsing, and compilation
- Python unit tests for ingestion behavior in pull requests
- DAG logs
- retries
- final mocked metrics and alert emission

## Common production challenges

- coordinating credentials across Composer, Cloud Run, and BigQuery
- controlling Composer cost
- ensuring the Composer environment has `dbt-bigquery` installed
- handling reprocessing without a full refresh strategy
- versioning ingestion containers without drift between application code and infrastructure
- scaling the CI/CD approach as more integrations are added
