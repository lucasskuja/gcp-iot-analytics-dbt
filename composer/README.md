# Composer Deployment Layout

Esta pasta representa o artefato de deploy para o bucket do Cloud Composer.

Estrutura:

- `dags/`: DAGs e dependencias locais necessarias para execucao no Composer
- `plugins/`: plugins e extensoes opcionais do Airflow
- `data/`: arquivos auxiliares sincronizaveis para o ambiente

O projeto dbt fica dentro de `dags/gcp_iot_analytics_dbt/dbt_project/` para que a DAG consiga executar `dbt-bigquery` sem depender de um checkout separado do repositorio dentro do Composer.
