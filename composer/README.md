# Composer Deployment Layout

This directory represents the deployment artifact synchronized to the Cloud Composer bucket.

It is structured to match the runtime expectations of a Composer environment rather than local source-code convenience alone. That makes deployment simpler and keeps orchestration assets self-contained.

## Structure

- `dags/`
  Airflow DAGs and local dependencies required at runtime.
- `plugins/`
  Optional Airflow plugins and extensions.
- `data/`
  Auxiliary files that should be synchronized with the environment.

## dbt co-location

The dbt project lives inside `dags/gcp_iot_analytics_dbt/dbt_project/` so the Airflow DAG can execute dbt directly from the Composer runtime without requiring a separate repository checkout inside the environment.

## Trade-off

Keeping dbt inside the Composer deployment artifact improves deployment cohesion, but it also means the synced bucket artifact must be versioned carefully and should not be treated as the primary development surface.
