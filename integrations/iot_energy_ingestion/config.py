from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    project_id: str = os.getenv("GCP_PROJECT_ID", "demo-project")
    region: str = os.getenv("GCP_REGION", "us-central1")
    raw_dataset: str = os.getenv("BQ_DATASET_RAW", "raw_iot_energy")
    analytics_dataset: str = os.getenv("BQ_DATASET_ANALYTICS", "analytics_iot_energy")
    raw_bucket: str = os.getenv("GCS_RAW_BUCKET", "smart-building-energy-raw")
    building_count: int = int(os.getenv("SIM_BUILDING_COUNT", "5"))
    devices_per_building: int = int(os.getenv("SIM_DEVICES_PER_BUILDING", "12"))
    late_arrival_ratio: float = float(os.getenv("SIM_LATE_ARRIVAL_RATIO", "0.05"))
    duplicate_ratio: float = float(os.getenv("SIM_DUPLICATE_RATIO", "0.03"))
    null_ratio: float = float(os.getenv("SIM_NULL_RATIO", "0.02"))


def get_settings() -> Settings:
    return Settings()
