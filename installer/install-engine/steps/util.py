"""Low-level helpers for the install engine: command execution, chroot, mounts.

A single MountTracker instance records every mount the engine makes so cleanup
can unwind them in reverse order even when a step fails midway.
"""
from __future__ import annotations

import os
import subprocess
from typing import Optional


class StepError(RuntimeError):
    """Raised when an install step fails unrecoverably."""


def run(cmd: list[str], *, env: Optional[dict] = None, check: bool = True,
        input_text: Optional[str] = None) -> subprocess.CompletedProcess:
    """Run a command, raising StepError with captured output on failure."""
    full_env = {**os.environ, **(env or {})}
    proc = subprocess.run(
        cmd, env=full_env, text=True, capture_output=True, input=input_text,
        check=False,
    )
    if check and proc.returncode != 0:
        raise StepError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\n"
            f"stdout: {proc.stdout.strip()}\nstderr: {proc.stderr.strip()}"
        )
    return proc


def run_stream(cmd: list[str], *, env: Optional[dict] = None, on_line=None) -> int:
    """Run a command streaming stdout line-by-line to `on_line(line)`.

    Returns the exit code. Used for long steps (debootstrap, apt) so progress
    can be surfaced live. stderr is merged into stdout.
    """
    full_env = {**os.environ, **(env or {})}
    proc = subprocess.Popen(
        cmd, env=full_env, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, bufsize=1,
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.rstrip("\n")
        if on_line and line:
            on_line(line)
    proc.wait()
    return proc.returncode


# Clean base environment for every chroot command. `env -i` starts from EMPTY,
# so host variables (TMPDIR, LC_ALL, …) never leak into the chroot — a leaked
# TMPDIR=/tmp/user/0 broke openssh-server's postinst (mktemp into a path that
# doesn't exist inside the chroot), and a leaked LC_ALL spammed locale warnings.
def _chroot_env(extra_env: Optional[dict]) -> dict:
    env = {
        "DEBIAN_FRONTEND": "noninteractive",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
        "TMPDIR": "/tmp",
        "HOME": "/root",
    }
    if extra_env:
        env.update(extra_env)
    return env


def chroot_run(target: str, cmd: list[str], *, check: bool = True,
               input_text: Optional[str] = None,
               extra_env: Optional[dict] = None) -> subprocess.CompletedProcess:
    """Run a command inside the target chroot with a clean (env -i) environment."""
    env_args = [f"{k}={v}" for k, v in _chroot_env(extra_env).items()]
    return run(["chroot", target, "env", "-i", *env_args, *cmd],
               check=check, input_text=input_text)


def chroot_stream(target: str, cmd: list[str], *, on_line=None,
                  extra_env: Optional[dict] = None) -> int:
    env_args = [f"{k}={v}" for k, v in _chroot_env(extra_env).items()]
    return run_stream(["chroot", target, "env", "-i", *env_args, *cmd],
                      on_line=on_line)


def write_file(path: str, content: str, *, mode: int = 0o644) -> None:
    """Write text to a file, creating parent dirs, with explicit permissions."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)
    os.chmod(path, mode)


class MountTracker:
    """Tracks mounts so they can be unwound in reverse order during cleanup."""

    def __init__(self):
        self._mounts: list[str] = []

    def mount(self, source: str, target: str, *, fstype: Optional[str] = None,
              bind: bool = False, options: Optional[str] = None) -> None:
        os.makedirs(target, exist_ok=True)
        cmd = ["mount"]
        if bind:
            cmd.append("--bind")
        if fstype:
            cmd += ["-t", fstype]
        if options:
            cmd += ["-o", options]
        cmd += [source, target]
        run(cmd)
        self._mounts.append(target)

    def unmount_all(self) -> None:
        for target in reversed(self._mounts):
            run(["umount", "-l", target], check=False)
        self._mounts.clear()
