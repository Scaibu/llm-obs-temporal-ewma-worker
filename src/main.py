"""
Root application bootstrap, DI wiring, and runner for temporal-ewma-worker.
Adheres strictly to 0-package-folder-writing-rule.md section 1.4: src/main.py.
Comment-free function bodies in accordance with rule (6).
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from temporalio.client import Client
from temporalio.worker import Worker

from features.ewma_compute.service import EwmaService
from worker.workflows import (
    EwmaBaselineUpdate,
    WeeklyIntegrityCheck,
    RetroactivePriceCorrection,
)


def get_worker_configuration() -> dict[str, str]:
    return {
        "temporal_host": os.getenv("TEMPORAL_HOST", "localhost:7233"),
        "temporal_namespace": os.getenv("TEMPORAL_NAMESPACE", "default"),
        "temporal_task_queue": os.getenv("TEMPORAL_TASK_QUEUE", "ewma-tasks"),
    }


async def run_worker() -> None:
    config = get_worker_configuration()
    client = await Client.connect(
        config["temporal_host"],
        namespace=config["temporal_namespace"],
    )

    worker = Worker(
        client,
        task_queue=config["temporal_task_queue"],
        workflows=[
            EwmaBaselineUpdate,
            WeeklyIntegrityCheck,
            RetroactivePriceCorrection,
        ],
        activities=[],
    )
    await worker.run()


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    if str(repo_root / "src") not in sys.path:
        sys.path.insert(0, str(repo_root / "src"))

    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
