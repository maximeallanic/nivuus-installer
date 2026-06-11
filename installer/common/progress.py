"""Progress event protocol shared by the install engine and the web portal.

The engine emits newline-delimited JSON ("jsonl") progress events. They are
written to two sinks simultaneously:

  * a log file  (/run/nivuus-install/progress.jsonl) — durable backlog so a
    reconnecting WebSocket client can replay everything it missed;
  * stdout       — captured live by installer_runner.py in the portal process.

Each event is a dict: {"ts": <float|None>, "step": str, "pct": int,
"level": "info"|"warn"|"error"|"done", "msg": str}.

We deliberately avoid Date.now()-style timestamps inside the engine itself; the
runner stamps a monotonic counter so logs stay ordered without wall-clock deps.
"""
from __future__ import annotations

import json
import os
import sys
from typing import TextIO

# Overridable via env so the engine/portal can run outside the ISO (dev, tests,
# loopback installs) without writing to /run.
PROGRESS_DIR = os.environ.get("NIVUUS_PROGRESS_DIR", "/run/nivuus-install")
PROGRESS_FILE = os.path.join(PROGRESS_DIR, "progress.jsonl")
CONFIG_FILE = os.path.join(PROGRESS_DIR, "config.json")

VALID_LEVELS = ("info", "warn", "error", "done")


class ProgressEmitter:
    """Writes structured progress events to a log file and stdout."""

    def __init__(self, log_path: str = PROGRESS_FILE, stream: TextIO | None = None):
        self.log_path = log_path
        self.stream = stream if stream is not None else sys.stdout
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        # Truncate any stale log from a previous run.
        self._fh = open(log_path, "w", buffering=1)
        self._seq = 0

    def emit(self, step: str, pct: int, msg: str, level: str = "info") -> None:
        if level not in VALID_LEVELS:
            level = "info"
        self._seq += 1
        event = {
            "seq": self._seq,
            "step": step,
            "pct": max(0, min(100, int(pct))),
            "level": level,
            "msg": msg,
        }
        line = json.dumps(event, ensure_ascii=False)
        self._fh.write(line + "\n")
        try:
            self.stream.write(line + "\n")
            self.stream.flush()
        except (BrokenPipeError, ValueError):
            pass

    def info(self, step: str, pct: int, msg: str) -> None:
        self.emit(step, pct, msg, "info")

    def warn(self, step: str, pct: int, msg: str) -> None:
        self.emit(step, pct, msg, "warn")

    def error(self, step: str, pct: int, msg: str) -> None:
        self.emit(step, pct, msg, "error")

    def done(self, msg: str = "Installation complete — you can reboot now.") -> None:
        self.emit("done", 100, msg, "done")

    def close(self) -> None:
        try:
            self._fh.close()
        except OSError:
            pass


def read_backlog(log_path: str = PROGRESS_FILE) -> list[dict]:
    """Read all events emitted so far (for a reconnecting client)."""
    events: list[dict] = []
    try:
        with open(log_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return events
