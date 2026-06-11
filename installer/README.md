# Nivuus Installer

A bootable ISO that installs Nivuus from a **web wizard served over a WiFi
hotspot**. Boot the USB stick on the target machine, connect a phone/laptop to
the `Nivuus-Setup-XXXX` WiFi (password shown on the server console), and the
configuration page opens automatically. Pick the disk, network and features,
press *Installer*, then reboot into a configured Nivuus server.

## How it works

```
 live boot (RAM)
   │
   ├─ nivuus-ap.service   → bring-up-ap.sh
   │      detects an AP-capable WiFi card, starts hostapd + dnsmasq on
   │      10.42.0.1/24 with a captive DNS. No WiFi? → Ethernet DHCP fallback.
   │
   └─ nivuus-portal.service → webapp/main.py (FastAPI on :80)
          serves the wizard, detects hardware, and on submit spawns…
                │
                └─ install-engine/run.py
                       partition → debootstrap → base config → kernel/GRUB →
                       apply Nivuus features (reuses /opt/nivuus/install.sh) →
                       validate. Progress streams back over a WebSocket.
```

The live root runs entirely in RAM; the engine debootstraps Debian onto the
**target disk** — the live image is never written to disk.

## Layout

| Path | Role |
|------|------|
| `common/hardware.py` | Generic hardware detection (disks, NICs, WiFi AP-capability, GPU IDs for VFIO, CPU topology → `isolcpus`). |
| `common/progress.py` | Structured progress-event protocol (jsonl log + stdout) shared by engine and portal. |
| `install-engine/run.py` | Orchestrator: scripted debootstrap install, emits progress. |
| `install-engine/steps/` | `partition`, `debootstrap`, `chroot_base`, `bootloader`, `features`, `validate`. |
| `install-engine/templates/` | Jinja2 configs: NM bridges, VLAN, PPPoE, hostapd. |
| `webapp/` | FastAPI portal: `main.py` (routes + `/ws/progress`), `models.py` (Pydantic), `installer_runner.py`, `static/` + `templates/` wizard. |
| `ap/` | Hotspot bring-up: `bring-up-ap.sh`, `hostapd-setup.conf.tmpl`. |
| `iso-build/` | live-build config, hooks (venv + enable services), `build.sh`. |

The installer **reuses the repo's own scripts** rather than duplicating logic:
`install.sh` (now `NIVUUS_DIR`-relative and `--non-interactive`-aware, with
`NIVUUS_ISOLCPUS` / `NIVUUS_VFIO_IDS` / `NIVUUS_IN_CHROOT` env hooks),
`scripts/optimize-cpu-thermal.sh`, `scripts/validate-install.sh`. The whole repo
is copied into the target at `/opt/nivuus`.

## Build the ISO

```bash
sudo apt-get install live-build        # build host (root)
cd installer
sudo make build-iso                    # → iso-build/*.iso
# include the prebuilt MQTT .deb: BUILD_MQTT_DEB=1 sudo -E make build-iso
```

## Test without rebuilding the ISO

```bash
# Web portal locally on :8080 (uses this machine's real hardware in the wizard)
make test-portal

# Engine against a loopback disk image (root) — safe, no real disk touched
truncate -s 16G /tmp/t.img
LOOP=$(sudo losetup --find --show /tmp/t.img)
# edit config.json's disk.path to $LOOP, then:
sudo NIVUUS_PROGRESS_DIR=/tmp/p python3 install-engine/run.py \
     --config config.json --target /tmp/mnt --nivuus-src .. --stop-after partition
sudo losetup -d $LOOP

# Boot the built ISO in QEMU (UEFI); portal reachable at http://localhost:8080
make test-vm
```

`--stop-after {partition,debootstrap,base,bootloader,features}` halts the engine
early for staged testing.

## Notes / limitations

- **WiFi AP can't be emulated in QEMU**; test the hotspot on real hardware via a
  USB stick. In the VM the portal is reached over the Ethernet fallback.
- The portal binds port 80 and runs the engine as root — it is meant to run only
  inside the throwaway live environment.
- Bookworm ships pydantic v1; the portal needs v2, so the live image builds a
  Python venv from `webapp/requirements.txt` (hook `0500-nivuus-venv`).
