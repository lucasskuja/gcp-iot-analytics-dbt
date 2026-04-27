from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

try:
    from .config import get_settings
except ImportError:
    from config import get_settings


@dataclass
class SensorEvent:
    ingestion_batch_id: str
    event_id: str
    device_id: str
    building_id: str
    timestamp: str
    energy_consumption: float | None
    temperature: float | None
    status: str
    ingested_at: str
    source_file: str


def build_devices(building_count: int, devices_per_building: int) -> list[tuple[str, str]]:
    devices: list[tuple[str, str]] = []
    for building_num in range(1, building_count + 1):
        building_id = f"BLD-{building_num:03d}"
        for device_num in range(1, devices_per_building + 1):
            device_id = f"{building_id}-DEV-{device_num:03d}"
            devices.append((building_id, device_id))
    return devices


def generate_base_events(execution_dt: datetime, intervals: int) -> list[SensorEvent]:
    settings = get_settings()
    devices = build_devices(settings.building_count, settings.devices_per_building)
    batch_id = execution_dt.strftime("%Y%m%d%H%M%S")
    source_file = f"iot_energy_{batch_id}.jsonl"
    ingested_at = datetime.now(timezone.utc).isoformat()
    events: list[SensorEvent] = []

    for building_id, device_id in devices:
        baseline = random.uniform(2.0, 6.0)
        for idx in range(intervals):
            event_time = execution_dt - timedelta(minutes=15 * idx)
            energy = round(max(0.05, random.gauss(baseline, 1.2)), 3)
            temperature = round(random.gauss(23.5, 3.5), 2)
            status = "offline" if random.random() < 0.04 else "online"
            event_id = f"{device_id}_{event_time.strftime('%Y%m%d%H%M')}"
            events.append(
                SensorEvent(
                    ingestion_batch_id=batch_id,
                    event_id=event_id,
                    device_id=device_id,
                    building_id=building_id,
                    timestamp=event_time.isoformat(),
                    energy_consumption=energy,
                    temperature=temperature,
                    status=status,
                    ingested_at=ingested_at,
                    source_file=source_file,
                )
            )
    return events


def inject_data_quality_issues(events: list[SensorEvent]) -> list[SensorEvent]:
    settings = get_settings()
    mutated = list(events)

    duplicate_count = max(1, int(len(mutated) * settings.duplicate_ratio))
    null_count = max(1, int(len(mutated) * settings.null_ratio))
    late_count = max(1, int(len(mutated) * settings.late_arrival_ratio))

    duplicates = [replace(event) for event in random.sample(mutated, duplicate_count)]
    mutated.extend(duplicates)

    for event in random.sample(mutated, null_count):
        if random.random() < 0.5:
            event.temperature = None
        else:
            event.energy_consumption = None

    for event in random.sample(mutated, null_count):
        event.energy_consumption = round(-1 * random.uniform(0.1, 3.0), 3)

    for event in random.sample(mutated, late_count):
        ts = datetime.fromisoformat(event.timestamp)
        event.timestamp = (ts - timedelta(hours=6)).isoformat()

    return mutated


def write_jsonl(events: Iterable[SensorEvent], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(asdict(event)) + "\n")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate IoT energy events with data quality issues.")
    parser.add_argument("--execution-date", required=True, help="Execution datetime in ISO format.")
    parser.add_argument("--intervals", type=int, default=96, help="15-minute intervals per device.")
    parser.add_argument("--output-dir", default="data", help="Directory where JSONL files will be written.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    execution_dt = datetime.fromisoformat(args.execution_date)
    events = generate_base_events(execution_dt=execution_dt, intervals=args.intervals)
    enriched = inject_data_quality_issues(events)
    batch_id = execution_dt.strftime("%Y%m%d%H%M%S")
    output_path = Path(args.output_dir) / f"iot_energy_{batch_id}.jsonl"
    write_jsonl(enriched, output_path)
    print(output_path.resolve())


if __name__ == "__main__":
    main()
