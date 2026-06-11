"""Step 9: post-install validation inside the chroot.

Runtime kernel checks (isolcpus active, IOMMU groups) cannot pass before the
first real boot, so we run the repo's validate-install.sh in a tolerant mode and
surface its output as warnings rather than hard failures.
"""
from __future__ import annotations

import os

from .util import chroot_run


def validate(config: dict, target: str, nivuus_dir: str, emit) -> None:
    emit.info("validate", 97, "Running post-install validation…")
    script = os.path.join(target, nivuus_dir.lstrip("/"), "scripts",
                          "validate-install.sh")
    if not os.path.exists(script):
        emit.warn("validate", 98, "validate-install.sh not found; skipping.")
        return

    result = chroot_run(
        target, ["bash", f"{nivuus_dir}/scripts/validate-install.sh"],
        check=False,
    )
    # The validator's runtime checks will largely report "needs reboot" here.
    for line in (result.stdout or "").splitlines()[-15:]:
        if line.strip():
            emit.info("validate", 98, line[:120])
    emit.info("validate", 99,
              "Validation finished (kernel-runtime checks re-run after reboot).")
