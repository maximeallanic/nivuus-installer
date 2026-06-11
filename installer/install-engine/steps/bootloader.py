"""Step 7: install the kernel and GRUB (UEFI) inside the chroot.

The Nivuus-specific kernel cmdline (isolcpus / IOMMU / vfio-pci.ids) is applied
later by the features step via install.sh; here we just get a bootable system.
"""
from __future__ import annotations

import os

from .util import StepError, chroot_run, chroot_stream, write_file


def install_bootloader(config: dict, target: str, fs: dict, emit) -> None:
    emit.info("bootloader", 70, "Installing kernel and GRUB (UEFI)…")

    chroot_run(target, ["apt-get", "update"])

    packages = ["linux-image-amd64", "grub-efi-amd64", "efibootmgr",
                "firmware-linux-free"]
    code = chroot_stream(
        target,
        ["apt-get", "install", "-y", "--no-install-recommends", *packages],
        on_line=lambda l: emit.info("bootloader", 74, l[:120]),
    )
    if code != 0:
        raise StepError("failed to install kernel/grub packages")

    # Non-free firmware so real NICs/WiFi work on first boot (generic installer).
    # Non-fatal: names vary across releases and not every box needs them.
    emit.info("bootloader", 76, "Installing device firmware (best-effort)…")
    chroot_run(
        target,
        ["apt-get", "install", "-y", "--no-install-recommends",
         "firmware-linux", "firmware-realtek", "firmware-iwlwifi",
         "firmware-misc-nonfree"],
        check=False,
    )

    # Default GRUB cmdline; the features step appends Nivuus kernel params.
    write_file(
        os.path.join(target, "etc/default/grub"),
        "GRUB_DEFAULT=0\nGRUB_TIMEOUT=3\n"
        'GRUB_DISTRIBUTOR="Nivuus"\n'
        'GRUB_CMDLINE_LINUX_DEFAULT="quiet"\n'
        'GRUB_CMDLINE_LINUX=""\n',
    )

    emit.info("bootloader", 78, "Writing GRUB to the EFI partition…")
    code = chroot_run(
        target,
        ["grub-install", "--target=x86_64-efi", "--efi-directory=/boot/efi",
         "--bootloader-id=Nivuus", "--recheck"],
        check=False,
    )
    if code.returncode != 0:
        # Fall back to removable-media path for firmware that ignores NVRAM.
        emit.warn("bootloader", 78, "grub-install NVRAM failed; using removable path.")
        chroot_run(
            target,
            ["grub-install", "--target=x86_64-efi", "--efi-directory=/boot/efi",
             "--bootloader-id=Nivuus", "--removable", "--recheck"],
        )
    chroot_run(target, ["update-grub"])
