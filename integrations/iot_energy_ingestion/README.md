# IoT Energy Ingestion

Integracao batch executada via `Cloud Run Job`.

Responsabilidades:

- gerar eventos IoT sinteticos
- introduzir problemas reais de qualidade
- gravar o raw no `GCS`
- carregar os eventos no `BigQuery`

Entrypoint:

```bash
python run_ingestion.py --execution-date 2026-04-26T10:00:00 --intervals 96 --output-dir /tmp/iot-energy-data
```
