"""Supervises the install-engine subprocess and exposes its progress.

The engine writes newline-delimited JSON progress events to a durable log
(/run/nivuus-install/progress.jsonl). The portal does not need to pipe the
engine's stdout: any number of WebSocket clients tail that file independently,
which gives reconnection-with-backlog for free.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from common.progress import PROGRESS_DIR, PROGRESS_FILE, CONFIG_FILE, read_backlog

ENGINE_RUN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "install-engine", "run.py",
)


class InstallRunner:
    """Singleton-ish supervisor for the install engine subprocess."""

    def __init__(self):
        self._proc: subprocess.Popen | None = None

    # -- lifecycle ---------------------------------------------------------- #
    def is_running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def start(self, config: dict, *, nivuus_src: str = "/opt/nivuus-src",
              target: str = "/mnt/target") -> None:
        if self.is_running():
            raise RuntimeError("an installation is already in progress")

        os.makedirs(PROGRESS_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as fh:
            json.dump(config, fh, indent=2)
        # Fresh progress log for this run.
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)

        self._proc = subprocess.Popen(
            [sys.executable, ENGINE_RUN,
             "--config", CONFIG_FILE,
             "--target", target,
             "--nivuus-src", nivuus_src],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    def status(self) -> dict:
        """Coarse run state for HTTP polling / page reloads."""
        events = read_backlog()
        terminal = next(
            (e for e in reversed(events) if e.get("level") in ("done", "error")),
            None,
        )
        if terminal:
            state = "done" if terminal["level"] == "done" else "error"
        elif self.is_running() or events:
            state = "running"
        else:
            state = "idle"
        return {
            "state": state,
            "running": self.is_running(),
            "last": events[-1] if events else None,
            "event_count": len(events),
        }


def events_since(seq: int) -> list[dict]:
    """Return progress events with seq greater than `seq` (for incremental tail)."""
    return [e for e in read_backlog() if e.get("seq", 0) > seq]
