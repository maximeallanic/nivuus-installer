"""Step 1-2: partition and format the target disk (GPT / UEFI), then mount it.

Layout (whole-disk, UEFI):
    part1  ESP   512 MiB  FAT32  -> /boot/efi
    part2  root  rest     ext4   -> /            (or LVM PV if use_lvm)

Returns a dict describing the created filesystems so later steps (fstab,
bootloader) can reference UUIDs and the EFI partition.
"""
from __future__ import annotations

import os
import time

from .util import StepError, run, MountTracker


def _partition_path(disk: str, num: int) -> str:
    # nvme0n1 -> nvme0n1p1 ; sda -> sda1
    if disk[-1].isdigit():
        return f"{disk}p{num}"
    return f"{disk}{num}"


def _wait_for(path: str, timeout: float = 10.0) -> None:
    """Wait for a device node to appear after partitioning."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if os.path.exists(path):
            return
        run(["udevadm", "settle"], check=False)
        time.sleep(0.3)
    raise StepError(f"device {path} did not appear after partitioning")


def partition_and_format(config: dict, target: str, mounts: MountTracker,
                         emit) -> dict:
    disk_cfg = config.get("disk", {})
    disk = disk_cfg.get("path")
    if not disk or not os.path.exists(disk):
        raise StepError(f"target disk not found: {disk!r}")
    use_lvm = bool(disk_cfg.get("use_lvm"))

    emit.info("partition", 2, f"Wiping and partitioning {disk}…")
    # Tear down any existing signatures / mounts on the disk first.
    run(["wipefs", "-a", disk], check=False)
    run(["sgdisk", "--zap-all", disk], check=False)

    # GPT: ESP + root.
    run(["sgdisk",
         "-n", "1:0:+512MiB", "-t", "1:ef00", "-c", "1:EFI",
         "-n", "2:0:0", "-t", ("2:8e00" if use_lvm else "2:8300"), "-c", "2:nivuus",
         disk])
    run(["partprobe", disk], check=False)

    esp = _partition_path(disk, 1)
    p2 = _partition_path(disk, 2)
    _wait_for(esp)
    _wait_for(p2)

    emit.info("partition", 6, "Creating filesystems…")
    run(["mkfs.fat", "-F32", "-n", "EFI", esp])

    if use_lvm:
        run(["pvcreate", "-ff", "-y", p2])
        run(["vgcreate", "nivuus", p2])
        run(["lvcreate", "-l", "100%FREE", "-n", "root", "nivuus"])
        root_dev = "/dev/nivuus/root"
        _wait_for(root_dev)
    else:
        root_dev = p2
    run(["mkfs.ext4", "-F", "-L", "nivuus-root", root_dev])

    emit.info("partition", 8, f"Mounting target on {target}…")
    mounts.mount(root_dev, target)
    mounts.mount(esp, os.path.join(target, "boot/efi"))

    return {
        "disk": disk,
        "esp": esp,
        "root_dev": root_dev,
        "use_lvm": use_lvm,
    }
