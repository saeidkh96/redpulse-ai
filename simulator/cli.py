import argparse
import time
from datetime import datetime, timedelta, timezone

from simulator.client import RedPulseClient
from simulator.config import SimulatorConfig
from simulator.engine import CNCSimulator
from simulator.profiles.degradation import (
    MILD_DEGRADATION,
    MODERATE_DEGRADATION,
    NORMAL_DEGRADATION,
    SEVERE_DEGRADATION,
)


DEGRADATION_PROFILES = {
    "normal": NORMAL_DEGRADATION,
    "mild": MILD_DEGRADATION,
    "moderate": MODERATE_DEGRADATION,
    "severe": SEVERE_DEGRADATION,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="RedPulse AI CNC telemetry simulator"
    )

    parser.add_argument(
        "--machine-id",
        required=True,
        help="Machine UUID registered in RedPulse",
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=10,
        help="Number of snapshots to generate",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between snapshots",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )

    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8001",
        help="RedPulse API base URL",
    )

    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Generate samples without real-time waiting",
    )

    parser.add_argument(
        "--degradation",
        choices=sorted(DEGRADATION_PROFILES.keys()),
        default="normal",
        help="Behavior degradation profile",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.samples < 1:
        parser.error("--samples must be at least 1")

    if args.interval <= 0:
        parser.error("--interval must be greater than 0")

    config = SimulatorConfig(
        machine_id=args.machine_id,
        seed=args.seed,
        sampling_interval_seconds=args.interval,
    )

    degradation = DEGRADATION_PROFILES[
        args.degradation
    ]

    simulator = CNCSimulator(
        config,
        degradation=degradation,
    )

    client = RedPulseClient(
        base_url=args.base_url
    )

    start_time = datetime.now(
        timezone.utc
    )

    total_inserted = 0

    print(
        f"Starting simulation: "
        f"machine={args.machine_id}, "
        f"samples={args.samples}, "
        f"degradation={args.degradation}"
    )

    for index in range(args.samples):
        timestamp = (
            start_time
            + timedelta(
                seconds=index * args.interval
            )
        )

        snapshot = simulator.generate_snapshot(
            timestamp
        )

        inserted = client.send_snapshot(
            snapshot
        )

        total_inserted += inserted

        print(
            f"[{index + 1}/{args.samples}] "
            f"{timestamp.isoformat()} "
            f"inserted={inserted}"
        )

        if (
            not args.no_wait
            and index < args.samples - 1
        ):
            time.sleep(args.interval)

    print(
        f"Simulation complete: "
        f"snapshots={args.samples}, "
        f"measurements={total_inserted}, "
        f"degradation={args.degradation}"
    )


if __name__ == "__main__":
    main()
