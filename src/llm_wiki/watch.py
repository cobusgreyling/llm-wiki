"""Watch raw/ for new files that need ingest."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from .ingest import get_ingest_status


def watch_raw(
    root: Path,
    *,
    interval: float = 2.0,
    once: bool = False,
    on_pending: Callable[[str, str], None] | None = None,
) -> None:
    """Poll raw/ and report pending ingest files."""
    seen_pending: set[str] = set()

    while True:
        statuses = get_ingest_status(root)
        pending = [s.raw_file for s in statuses if s.status == "pending"]
        new_pending = [f for f in pending if f not in seen_pending]

        if new_pending:
            for raw_file in new_pending:
                message = f"New raw file pending ingest: raw/{raw_file}"
                if on_pending:
                    on_pending(message, raw_file)
                else:
                    print(message)
            seen_pending.update(new_pending)

        if once:
            return

        time.sleep(interval)
