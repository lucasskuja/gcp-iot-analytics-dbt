from __future__ import annotations

from types import SimpleNamespace

from integrations.iot_energy_ingestion import run_ingestion


def test_main_calls_generator_and_loader(monkeypatch) -> None:
    captured_calls: list[list[str]] = []

    monkeypatch.setattr(
        run_ingestion,
        "parse_args",
        lambda: SimpleNamespace(
            execution_date="2026-04-26T10:00:00",
            intervals=8,
            output_dir="/tmp/iot-energy-data",
        ),
    )

    def fake_run(command: list[str], check: bool, capture_output: bool = False, text: bool = False):
        captured_calls.append(command)
        if "generate_iot_data.py" in command[1]:
            return SimpleNamespace(stdout="/tmp/iot-energy-data/iot_energy_20260426100000.jsonl\n")
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(run_ingestion.subprocess, "run", fake_run)

    run_ingestion.main()

    assert len(captured_calls) == 2
    assert "generate_iot_data.py" in captured_calls[0][1]
    assert captured_calls[1][-1] == "/tmp/iot-energy-data/iot_energy_20260426100000.jsonl"
