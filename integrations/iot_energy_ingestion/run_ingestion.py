from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full ingestion pipeline.")
    parser.add_argument("--execution-date", required=True, help="Execution datetime in ISO format.")
    parser.add_argument("--intervals", type=int, default=96, help="15-minute intervals per device.")
    parser.add_argument("--output-dir", default="/tmp/iot-energy-data", help="Directory for generated files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).parent
    generate_cmd = [
        sys.executable,
        str(base_dir / "generate_iot_data.py"),
        "--execution-date",
        args.execution_date,
        "--intervals",
        str(args.intervals),
        "--output-dir",
        args.output_dir,
    ]
    result = subprocess.run(generate_cmd, check=True, capture_output=True, text=True)
    generated_file = result.stdout.strip().splitlines()[-1]

    load_cmd = [
        sys.executable,
        str(base_dir / "load_to_bigquery.py"),
        "--file-path",
        generated_file,
    ]
    subprocess.run(load_cmd, check=True)


if __name__ == "__main__":
    main()
