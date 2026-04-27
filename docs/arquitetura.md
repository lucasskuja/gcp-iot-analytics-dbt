# Arquitetura da Plataforma de Dados

## Objetivo

Esta plataforma simula um ambiente moderno de dados no GCP para monitoramento energetico de dispositivos IoT em predios inteligentes. O foco esta em mostrar decisoes de arquitetura, trade-offs, preocupacao com custo e um desenho de deploy mais crivel para producao.

## Estrutura operacional do repositorio

O repositorio agora separa melhor o que e codigo fonte e o que e artefato de deploy:

- `integrations/`: codigo Python containerizado para jobs de integracao
- `composer/`: conteudo sincronizado para o bucket do `Cloud Composer`
- `infra/terraform/`: infraestrutura GCP
- `docs/`: documentacao arquitetural

Dentro de `composer/`, a estrutura segue o formato do bucket do Composer:

- `composer/dags/`
- `composer/plugins/`
- `composer/data/`

O projeto dbt foi colocado em `composer/dags/gcp_iot_analytics_dbt/dbt_project/` para que a DAG consiga rodar `dbt-bigquery` no proprio ambiente do Composer sem depender de checkout externo do repositorio.

Dentro de `integrations/`, cada pasta representa uma unidade de deploy independente. Isso aproxima o repositorio de um setup real em que diferentes jobs de integracao podem ter ciclos de release proprios.

## Desenho de producao adotado

1. `Cloud Composer` agenda e orquestra o pipeline.
2. A DAG executa um `Cloud Run Job` para ingestao batch, atualmente empacotado em `integrations/iot_energy_ingestion/`.
3. O job gera os dados IoT sinteticos, grava o raw no `GCS` e carrega o raw no `BigQuery`.
4. A DAG executa `dbt deps`, `dbt run`, `dbt snapshot` e `dbt test` usando o projeto dbt que foi sincronizado para o bucket do Composer.
5. O pipeline finaliza com logs, metricas basicas e alertas mockados.

## Por que cada tecnologia foi escolhida

### Cloud Run Jobs

Foi escolhido para a ingestao porque o workload e batch e finito. Isso combina melhor com `Jobs` do que com um servico HTTP.

Vantagens:

- serverless
- bom para cargas agendadas
- escala simples
- separa claramente o runtime da ingestao

Trade-offs:

- exige build e versionamento de imagem
- observabilidade e debugging dependem de logs do GCP
- quando ha varias integracoes, e preciso organizar bem versionamento e ownership por pasta

### Integrations folder per job

Foi escolhido um layout com uma pasta por integracao para facilitar CI por path.

Vantagens:

- cada job pode ter seu proprio Dockerfile e dependencias
- CI consegue fazer deploy seletivo
- ownership e manutencao ficam mais claros

Trade-offs:

- mais repeticao estrutural entre integracoes
- exige padroes claros para evitar divergencia excessiva entre jobs

### Cloud Composer

Foi escolhido porque o caso pede coordenacao entre ingestao, transformacao e testes com dependencias explicitas.

Vantagens:

- Airflow e reconhecido pelo mercado
- retries, sensores, dependencias e logs sao maduros
- integra bem com operadores GCP

Trade-offs:

- custo fixo alto
- operacao mais pesada que solucoes serverless puras
- precisa de disciplina para sincronizar corretamente o conteudo do bucket de DAGs

### BigQuery

Permanece como warehouse e engine de processamento analitico.

Vantagens:

- executa o dbt diretamente
- integra com GCS
- performance boa para analytics
- baixo overhead operacional

Trade-offs:

- custo por query depende muito de modelagem e filtros
- exige disciplina com incremental, particionamento e clustering

### dbt-bigquery

Foi escolhido porque organiza modelagem analitica, testes, snapshots e documentacao de forma clara.

Vantagens:

- organiza a transformacao em camadas
- melhora rastreabilidade
- facilita testes e documentacao

Trade-offs:

- depende de um runtime com dbt instalado
- por estar embutido no deploy do Composer, requer versionamento cuidadoso desse artefato

### GCS

Mantem a camada raw barata, auditavel e reprocessavel.

Trade-offs:

- adiciona uma etapa a mais entre geracao e consumo analitico
- exige politica de retencao e organizacao de paths

## Principais trade-offs do layout Composer

### Por que colocar o dbt dentro de `composer/dags`

Motivo:

- a DAG e o dbt ficam co-localizados
- o bucket do Composer vira um artefato autocontido
- o CI pode sincronizar tudo com base em uma unica pasta

Trade-off:

- aumenta o tamanho do artefato sincronizado
- exige cuidado para nao tratar o bucket do Composer como repositorio primario de desenvolvimento

### Por que manter CI de sync por paths

Motivo:

- reduz deploys desnecessarios
- separa melhor mudancas de orquestracao de mudancas de infra

Trade-off:

- requer convencao clara de onde cada tipo de arquivo deve morar no repositorio

## Qualidade e observabilidade

O projeto simula problemas reais:

- duplicidades
- nulos
- energia negativa
- eventos atrasados
- instabilidade de status

Controles incluidos:

- testes `not null`, `unique`, `accepted_values`
- testes customizados de freshness e threshold de nulos
- CI de `dbt` com validacao de dependencias, parse e compile
- testes unitarios da integracao Python em pull requests
- logs na DAG
- retries
- etapa final de metricas e alertas mockados

## Desafios comuns em producao

- sincronizar credenciais entre Composer, Cloud Run e BigQuery
- controlar custos do Composer
- garantir que o ambiente do Composer tenha o `dbt-bigquery` instalado
- lidar com reprocessamento sem full refresh
- versionar o container da ingestao sem drift entre codigo e infraestrutura
- escalar a estrategia de CI quando houver varias integracoes em paralelo
