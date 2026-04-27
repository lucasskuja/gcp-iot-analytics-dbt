from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from integrations.iot_energy_ingestion import generate_iot_data


def test_build_devices_creates_expected_pairs() -> None:
    devices = generate_iot_data.build_devices(building_count=2, devices_per_building=3)

    assert len(devices) == 6
    assert devices[0] == ("BLD-001", "BLD-001-DEV-001")
    assert devices[-1] == ("BLD-002", "BLD-002-DEV-003")


def test_generate_base_events_respects_device_and_interval_count(monkeypatch) -> None:
    monkeypatch.setattr(
        generate_iot_data,
        "get_settings",
        lambda: SimpleNamespace(
            building_count=2,
            devices_per_building=2,
        ),
    )

    execution_dt = generate_iot_data.datetime.fromisoformat("2026-04-26T10:00:00")
    events = generate_iot_data.generate_base_events(execution_dt=execution_dt, intervals=4)

    assert len(events) == 16
    assert events[0].building_id.startswith("BLD-")
    assert events[0].device_id.startswith(events[0].building_id)
    assert events[0].source_file.endswith(".jsonl")


def test_write_jsonl_creates_a_valid_file(tmp_path: Path) -> None:
    event = generate_iot_data.SensorEvent(
        ingestion_batch_id="20260426100000",
        event_id="evt-1",
        device_id="BLD-001-DEV-001",
        building_id="BLD-001",
        timestamp="2026-04-26T10:00:00",
        energy_consumption=1.23,
        temperature=23.4,
        status="online",
        ingested_at="2026-04-26T10:01:00+00:00",
        source_file="iot_energy_20260426100000.jsonl",
    )

    output_file = tmp_path / "out" / "events.jsonl"
    result = generate_iot_data.write_jsonl([event], output_file)

    assert result.exists()
    payload = json.loads(result.read_text(encoding="utf-8").strip())
    assert payload["event_id"] == "evt-1"
    assert payload["energy_consumption"] == 1.23
