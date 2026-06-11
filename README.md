<div align="center">

# 🎮 Nivuus

### Turn a spare PC into a cloud-gaming powerhouse — set up entirely from your phone.

**Burn one USB stick. Boot it. Connect to its Wi‑Fi. Configure everything in a web page. Reboot into a fully-tuned server.**

No SSH. No config files. No 40-tab how-to. Just a wizard.

[![Build ISO](https://github.com/maximeallanic/nivuus-installer/actions/workflows/build-iso.yml/badge.svg)](https://github.com/maximeallanic/nivuus-installer/actions/workflows/build-iso.yml)
[![Latest ISO](https://img.shields.io/github/v/release/maximeallanic/nivuus-installer?label=download%20ISO)](https://github.com/maximeallanic/nivuus-installer/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Debian 12](https://img.shields.io/badge/base-Debian%2012-A81D33)
![UEFI](https://img.shields.io/badge/boot-UEFI-informational)

</div>

---

## Why Nivuus?

You've got hardware. Maybe an old gaming rig, a homelab box, a Frankenstein build with a spare GPU. Turning it into a real server means hours of `apt`, GRUB edits, IOMMU groups, hostapd configs, firewall zones, VFIO incantations… copy-pasted from a dozen blog posts that half-work.

**Nivuus collapses all of that into a boot-and-click experience.** It's a bootable installer that opens its own **Wi‑Fi hotspot** at boot. You join it from your laptop or phone, a **setup page pops up automatically** (captive-portal style), you pick your disk, your network, your features — hit *Install*, and watch a live progress bar. Reboot, and your machine is a tuned cloud-gaming + homelab server.

> Think "router setup wizard," but it installs an entire optimized Linux server.

---

## ⚡ Install in 3 steps

```
   ┌─────────────┐      ┌──────────────────────┐      ┌────────────────────┐
   │ 1. Flash USB │  →   │ 2. Boot + join Wi‑Fi  │  →  │ 3. Configure in web │
   │  the ISO     │      │  "Nivuus-Setup-XXXX"  │     │  page → Install     │
   └─────────────┘      └──────────────────────┘      └────────────────────┘
```

1. **Flash it.** Download the [latest ISO](https://github.com/maximeallanic/nivuus-installer/releases/latest) and write it to a USB stick (`dd`, Rufus, balenaEtcher… your call).
2. **Boot it.** Plug it into the target machine and boot (UEFI). A Wi‑Fi network **`Nivuus-Setup-XXXX`** appears — the password is shown right on the screen. No screen handy? It also serves the portal over Ethernet.
3. **Configure it.** Join the network from any device; the setup page opens on its own. Choose disk, hostname, account, internet (DHCP or PPPoE), Wi‑Fi, and which features to install. Press **Install**, watch the live log, reboot. Done. 🎉

No keyboard on the server. No monitor required. No prior Linux knowledge needed.

---

## 🧰 What you can build with it

Tick the boxes you want in the wizard — Nivuus installs and wires them up:

| Feature | What it gives you |
|---|---|
| 🖥️ **GPU passthrough gaming VM** | QEMU/KVM + VFIO, IOMMU, hugepages, 1:1 CPU pinning. Stream games (Moonlight/Parsec/RDP) from a Windows VM with a real GPU. |
| 🌡️ **Thermal tuning** | Smart P‑core/E‑core frequency + fan curves. Quiet, cool, and up to **‑60% idle power** — no throttling. |
| 🌐 **Full networking** | NetworkManager bridges (trusted / guest / VM), DHCP or **PPPoE** (fibre) with one form. |
| 📶 **Dual-band Wi‑Fi access point** | Your server becomes the Wi‑Fi too — `hostapd` 2.4 + 5 GHz, private + guest SSIDs. |
| 🛡️ **Firewall** | `firewalld` + `nftables` + `fail2ban`, sensible zones out of the box. |
| 🐳 **Docker stack** | One toggle for the container engine; bring your media/homelab stack (Plex, *arr suite, etc.). |
| 🏠 **Home Assistant + MQTT** | Smart-home hub plus a system-monitoring agent that surfaces your server in HA. |

**Everything is hardware-generic.** Nivuus auto-detects your CPU topology (computes `isolcpus`, no hardcoded core numbers), your discrete GPU (fills in `vfio-pci.ids` for you), your disks and NICs — so it works on *your* box, not just the author's.

---

## 📦 Download

Grab the prebuilt image from **[Releases](https://github.com/maximeallanic/nivuus-installer/releases/latest)** → `nivuus-installer-amd64.iso` (~720 MB, UEFI, hybrid). Verify with the published `.sha256`, flash, and go.

Every push to `main` also builds a fresh ISO in CI — download it from the [Actions](https://github.com/maximeallanic/nivuus-installer/actions) tab.

---

## 🔧 Build it yourself

Prefer to roll your own? It's one command on any Debian/Ubuntu box (or just let CI do it):

```bash
git clone https://github.com/maximeallanic/nivuus-installer.git
cd nivuus-installer/installer
sudo apt-get install -y live-build
sudo make build-iso          # → installer/iso-build/*.iso
```

Hack on the installer without rebuilding the ISO every time:

```bash
make test-portal             # run the web wizard locally on :8080
make test-vm                 # boot the built ISO in QEMU (UEFI)
# drive the install engine against a throwaway loopback disk:
sudo python3 install-engine/run.py --config cfg.json --target /mnt/t --stop-after partition
```

---

## 🩻 Under the hood

The live system runs entirely in RAM — your target disk is only touched when *you* hit Install.

```
 USB boot (live, in RAM)
   ├─ nivuus-ap.service     → opens the Wi‑Fi hotspot (hostapd + dnsmasq + captive DNS)
   │                          falls back to Ethernet if there's no AP-capable Wi‑Fi
   └─ nivuus-portal.service → FastAPI web wizard (hardware detection, live progress over WebSocket)
            │
            └─ install-engine → partition → debootstrap Debian 12 → kernel + GRUB (UEFI)
                                → apply your chosen features → done, reboot.
```

- **Web portal:** Python + FastAPI, zero-build vanilla front-end.
- **Install engine:** a clean, scripted `debootstrap` (no fragile preseed), streaming structured progress to your browser.
- **Reuse over reinvention:** the engine drops the whole project into `/opt/nivuus` on the new system and runs the same battle-tested scripts you'd run by hand.

Full architecture lives in [`installer/README.md`](installer/README.md).

---

## 🗺️ Repo layout

```
nivuus-installer/
├── installer/        ⭐ the bootable installer (web wizard + WiFi hotspot + engine)
│   ├── webapp/         FastAPI setup portal + wizard UI
│   ├── install-engine/ scripted debootstrap install pipeline
│   ├── ap/             Wi‑Fi hotspot bring-up
│   ├── iso-build/      live-build config (the ISO recipe)
│   └── common/         generic hardware detection + progress protocol
├── mqtt/             Home Assistant system-monitoring agent (TypeScript)
├── configs/          reference network / firewall / VM configs
├── scripts/          thermal tuning, validation, HA CLI helpers
├── docs/             deep-dive documentation
└── install.sh        the post-install tuner (run standalone too)
```

---

## 🛠️ Hardware & requirements

- **Target:** any x86‑64 machine that boots **UEFI**. A discrete GPU is needed only for the gaming-VM feature; everything else works without one.
- **Generic by design:** Intel hybrid (P/E) CPUs get optimal core isolation automatically, but plain CPUs work too.
- **Built on:** Debian 12 (Bookworm).
- **For the setup hotspot:** an AP-capable Wi‑Fi adapter is nice-to-have — without one, the wizard is served over Ethernet instead.

---

## 🤝 Contributing / hacking

PRs and tinkering very welcome — this is built for people who like to take things apart. Add a feature module, teach the wizard a new question, improve hardware detection. Start with [`installer/README.md`](installer/README.md) and the `make test-*` targets above.

> 🔐 **Heads-up:** this is a public, sanitized release. Anywhere you see `CHANGE_ME_*` or `<YOUR_*>` placeholders (Wi‑Fi passwords, PPPoE credentials, tokens), drop in your real values **locally** — never commit them.

---

## 📜 License

[MIT](LICENSE) — do whatever you want with it. Build something cool.

<div align="center">

**Got an old box and a spare GPU? Go flash a stick.** 🕹️

</div>
