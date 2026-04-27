# Integrations

Esta pasta agrupa os codigos de integracao executados fora do Composer, normalmente como `Cloud Run Jobs`.

Convencao sugerida:

- uma subpasta por integracao
- cada integracao com `Dockerfile`, `requirements.txt`, codigo Python e documentacao propria
- CI por path para build, push e atualizacao da imagem no runtime alvo

Exemplo atual:

- `iot_energy_ingestion/`: job responsavel por gerar dados IoT, gravar raw no GCS e carregar o BigQuery raw
