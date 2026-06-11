# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Instructions for Claude

**IMPORTANT**: Whenever you learn something important about this project (architecture decisions, critical bugs fixed, configuration patterns, etc.), immediately update this CLAUDE.md file. Keep it:
- **Compact**: Dense, relevant information only
- **No duplicates**: Remove redundant information
- **Up-to-date**: Reflect current project state

**BE PROACTIVE**: When working on the codebase, actively look for improvements or issues beyond the current scope. If you spot bugs, performance issues, code smells, security concerns, or optimization opportunities - signal them to the user and fix them. Don't wait to be asked.

## Project Overview

**Nivuus** is a cloud gaming server infrastructure with comprehensive system monitoring integration. The project consists of:

1. **MQTT System Agent** (`mqtt/`): TypeScript-based monitoring agent that publishes system metrics to Home Assistant via MQTT
2. **Infrastructure Configuration**: Scripts and configs for thermal optimization, VM management, networking, and firewall
3. **Home Assistant Integration**: Full domotics control of the gaming server
4. **Installer** (`installer/`): Bootable ISO that installs Nivuus via a web wizard served over a WiFi setup hotspot

## MQTT System Agent Architecture

### Core Design Patterns

The MQTT agent uses a **feature-based architecture** with class inheritance:

- **BaseFeature** (`mqtt/src/core/BaseFeature.ts`): Abstract base class that all monitoring features inherit from
- Each feature is self-contained with its own data collection, MQTT publishing, and Home Assistant discovery
- Features are registered in `mqtt/src/core/Agent.ts` and enabled/disabled via `mqtt/config/agent.yaml`

### Key Components

1. **Configuration System** (`mqtt/src/config.ts`):
   - Singleton ConfigManager loads `config/agent.yaml`
   - Provides fallback configuration if loading fails
   - **IMPORTANT**: Error fallback uses same `device_info.identifiers` and `base_topic` as normal config to maintain Home Assistant entity consistency

2. **MQTT Client** (`mqtt/src/mqtt/MqttClient.ts`):
   - Wrapper around `mqtt` npm package
   - Handles connection, reconnection, LWT (Last Will Testament)
   - All features use this wrapper, not the raw MQTT client

3. **Agent** (`mqtt/src/core/Agent.ts`):
   - Main orchestrator that initializes MQTT client and all enabled features
   - Publishes inline Home Assistant discovery for alerts and events
   - Maps feature names to their classes in `availableFeatures`

4. **Features** (`mqtt/src/features/`):
   - Each subdirectory represents a category (cpu, memory, disk, network, etc.)
   - Features must extend BaseFeature and implement abstract methods
   - Features self-register their Home Assistant entities via MQTT discovery

### MQTT Topic Structure

```
system_agent/                           # base_topic from config
├── {device_id}/                        # device_info.identifiers[0]
│   ├── status                          # Availability topic (online/offline)
│   ├── {feature_name}/                 # e.g., cpu_temperature
│   │   ├── {entity_id}/state           # Entity state
│   │   └── {entity_id}/attributes      # Entity attributes (JSON)
│   └── alert                           # Alert sensor
│   └── event                           # Event sensor

homeassistant/                          # HA Discovery prefix
└── {component}/{device_id}/{unique_id}/config
```

### Adding a New Feature

1. Create class extending BaseFeature in appropriate `src/features/` subdirectory
2. Implement required methods: `setupDiscovery()`, `update()`, `setupCommandHandlers()`
3. Add to `availableFeatures` map in `src/core/Agent.ts`
4. Add configuration to `config/agent.yaml`

## Installer Architecture (`installer/`)

Bootable **Debian live ISO** (built with `live-build`) that installs Nivuus onto
a target disk via a **web wizard served over a WiFi setup hotspot**. Flow: boot
USB → `nivuus-ap.service` opens AP `Nivuus-Setup-XXXX` (10.42.0.1, captive DNS;
falls back to Ethernet DHCP if no AP-capable WiFi) → `nivuus-portal.service`
(FastAPI :80) shows the wizard → on submit, `install-engine/run.py` does a
scripted debootstrap install. The live root runs in RAM; the engine never writes
the live image to disk. Full docs: `installer/README.md`.

**Components:**
- `installer/common/hardware.py` — generic detection (disks, NICs, WiFi
  AP-capability via `iw`, GPU vendor:device IDs for `vfio-pci.ids`, CPU topology
  → computed `isolcpus`/`nohz_full`, **not** hardcoded to the i9-12900K).
- `installer/common/progress.py` — jsonl progress protocol (durable backlog +
  stdout) shared by engine and portal; WebSocket clients tail it for free
  reconnection. Override dir via `NIVUUS_PROGRESS_DIR` (default `/run/nivuus-install`).
- `installer/install-engine/` — `run.py` orchestrator + `steps/` (partition,
  debootstrap, chroot_base, bootloader, features, validate). `--stop-after STEP`
  for staged testing. `templates/*.j2` render NM bridges, VLAN, PPPoE, hostapd.
- `installer/webapp/` — FastAPI portal: `main.py` (routes + `/ws/progress` +
  captive-detection endpoints), `models.py` (Pydantic v2 `InstallConfig`),
  `installer_runner.py`, `static/` + `templates/` wizard.
- `installer/ap/bring-up-ap.sh` — hotspot bring-up + captive nftables redirect.
- `installer/iso-build/` — live-build config; hook `0500-nivuus-venv` builds a
  pydantic-v2 venv (bookworm ships v1), hook `9000` enables the services.

**Reuse, don't duplicate:** the engine copies the whole repo to `/opt/nivuus` in
the target and **calls** `install.sh` inside the chroot. `install.sh` was made
installer-aware (backward-compatible): `NIVUUS_DIR` now resolves to the script's
own dir; env hooks `NIVUUS_ASSUME_YES`/`--non-interactive`, `NIVUUS_IN_CHROOT`
(skip runtime thermal apply), `NIVUUS_ISOLCPUS`, `NIVUUS_IOMMU`, `NIVUUS_VFIO_IDS`
(generic kernel params instead of the hardcoded `isolcpus=0-15`).

**Build & test:** `cd installer && sudo make build-iso` (needs `live-build`).
`make test-portal` (portal on :8080), `make test-vm` (QEMU UEFI, portal via
Ethernet fallback — WiFi AP isn't emulable in QEMU), engine on a loopback image
via `--stop-after`. The riskiest path (partition/format/mount) is validated; the
debootstrap path uses standard tooling.

## Development Commands

**Location**: All commands run from `mqtt/` directory

```bash
# Build TypeScript to JavaScript
npm run build

# Start the agent (requires build first)
npm start

# Run tests
npm test

# Package as executable (Linux x64)
npm run package:executable

# Package as Debian package
npm run package:deb

# Development utilities
./list-entities.sh              # List Home Assistant entities
./clean-entities.sh             # Clean MQTT retained messages
./clean-restart.sh              # Clean restart with entity cleanup
```

**IMPORTANT**: The project is in development mode - do NOT install packages unless explicitly required.

### Home Assistant CLI (`/usr/local/bin/ha`)

Bash CLI for the Home Assistant REST + WebSocket API. Covers entity state management, service calls, and full CRUD on automations, scripts, and dashboards. Uses `curl` for REST, embedded Python + `aiohttp` for WebSocket (traces, dashboards). Output is colorized with `jq` formatting.

**CRITICAL**: NEVER edit `.storage/` files directly. Always use the `ha` CLI to modify Home Assistant configuration (dashboards, automations, etc.). Direct file edits can corrupt HA state or be overwritten.

**Config**: `/root/.config/nivuus/ha.conf` (`HA_URL` + `HA_TOKEN`), falls back to env vars or localhost defaults.

```bash
# Entity & state management
ha states                              # List all entity states (JSON)
ha states <entity_id>                  # Get specific entity state
ha set <entity_id> <state> [attr_json] # Set entity state + optional attributes
ha call <entity_id> <action> [data]    # Shortcut: call service on entity (auto-detects domain)
ha service <domain> <service> [data]   # Call any HA service
ha history <entity_id> [duration]      # State history (duration: Nh/Nd/Nm, default 24h)
ha log                                 # View HA error log
ha config                              # Get HA configuration
ha events <type> [data]                # Fire a custom event
ha template '<jinja2>'                 # Render a Jinja2 template
ha raw <endpoint> [method] [data]      # Raw REST API call (any endpoint)

# Automations (REST + WebSocket for traces/categories)
ha automation list                     # Table: entity_id, state (on/off), last_triggered, category, name
ha automation get <entity_id>          # Get config JSON (uses config ID from attributes)
ha automation enable <entity_id>       # Turn on
ha automation disable <entity_id>      # Turn off
ha automation trigger <entity_id>      # Trigger immediately
ha automation edit <entity_id> <file|->  # Update config from file or stdin
ha automation rename <entity_id> <name>  # Rename automation (updates alias in config)
ha automation category <entity_id>     # Get current category
ha automation category <entity_id> <name>  # Set category (auto-creates if needed, uses WebSocket entity/category registry)
ha automation icon <entity_id>         # Get current icon
ha automation icon <entity_id> <icon>  # Set icon (mdi:...), use "" to remove
ha automation create <file|->          # Create new (auto-generates timestamp config ID)
ha automation delete <entity_id> [-y]  # Delete (-y skips confirmation)
ha automation trace <entity_id>        # Execution traces via WebSocket (timestamp, state, trigger)
ha automation reload                   # Reload YAML automations

# Scripts (REST + WebSocket for traces)
ha script list                         # Table: entity_id, state (off/running), last_triggered, name
ha script get <entity_id>              # Get config JSON (slug = object_id, no attributes lookup)
ha script trigger <entity_id>          # Run script (script.turn_on)
ha script edit <entity_id> <file|->    # Update config from file or stdin
ha script create <script_id> <file|->  # Create new (user provides slug, becomes script.<slug>)
ha script delete <entity_id> [-y]      # Delete (-y skips confirmation)
ha script trace <entity_id>            # Execution traces via WebSocket
ha script reload                       # Reload YAML scripts

# Scenes (REST - same pattern as automations)
ha scene list                          # Table: entity_id, friendly_name
ha scene get <entity_id>               # Get config via attributes.id lookup
ha scene activate <entity_id>          # Activate scene (with optional --transition N)
ha scene edit <entity_id> <file|->     # Update config from file or stdin
ha scene create <file|->               # Create new (auto-generates timestamp config ID)
ha scene delete <entity_id> [-y]       # Delete (-y skips confirmation)
ha scene reload                        # Reload YAML scenes

# Blueprints (WebSocket only)
ha blueprint list [domain]             # Table: path, name, domain (default: automation)
ha blueprint get <path> [domain]       # Get blueprint details from list result
ha blueprint import <url> [domain]     # Import from URL + auto-save
ha blueprint delete <path> [domain] [-y]  # Delete (-y skips confirmation)

# Dashboards (WebSocket only - Lovelace)
ha dashboard list                      # Table: url_path, title, mode, sidebar, admin
ha dashboard get [url_path]            # Get config JSON (default dashboard if omitted)
ha dashboard set <url_path> <file|->   # Update from file or stdin
ha dashboard delete <url_path> [-y]    # Delete (-y skips confirmation)
```

**Key implementation details**:
- Entity ID prefix is auto-added: `ha script get my_script` → looks up `script.my_script`
- Automations and scenes use a config ID stored in `attributes.id` (API lookup required); scripts use the object_id directly
- `automation create` and `scene create` auto-generate a timestamp ID; `script create` requires an explicit slug
- File arguments accept `-` for stdin: `echo '{"alias":"test"}' | ha script create my_id -`
- All delete commands prompt for confirmation unless `-y` is passed
- Blueprints default to `automation` domain; pass `script` as second arg for script blueprints
- `blueprint import` fetches + auto-saves via `blueprint/save` WebSocket call

## Deployment Workflow

**When a feature is complete**, follow this workflow to deploy:

```bash
cd mqtt/

# 1. Build the Debian package
npm run package:deb

# 2. Install the package
sudo dpkg -i mqtt-system-agent_1.0.0_amd64.deb

# 3. Restart the service to apply changes
sudo systemctl restart mqtt-system-agent.service

# 4. Check service status and logs
sudo systemctl status mqtt-system-agent.service
sudo journalctl -u mqtt-system-agent.service -f
```

## Configuration

### Main Config File

`mqtt/config/agent.yaml` contains:
- MQTT broker connection (host: 192.168.0.1, port: 1883)
- Device info (identifiers, name, model) - **must match error fallback in config.ts**
- Feature enable/disable flags and update intervals

### MQTT Connection for Testing

```bash
# Subscribe to all Home Assistant discovery messages
mosquitto_sub -h 192.168.0.1 -t "homeassistant/#" -v -u mqtt -P CHANGE_ME_MQTT_PASSWORD

# Subscribe to all agent state topics
mosquitto_sub -h 192.168.0.1 -t "system_agent/#" -v -u mqtt -P CHANGE_ME_MQTT_PASSWORD
```

## Code Style Guidelines

From `.github/copilot-instructions.md`:

- **File Organization**: Maximum 200 lines per file - split if larger
- **Architecture**: Use classes and inheritance extensively
- **Modularity**: Each file should be self-contained and minimal
- **Comments**: English only
- **Logging**: Use logger for debugging, remove logs when no longer needed
- **Workflow**: Build → Start → Check logs → Fix → Repeat
- **Autonomy**: Be proactive - execute commands without asking for approval
- **System Adaptation**: Understand and adapt to the actual machine configuration

## Home Assistant Integration

The agent creates these entities in Home Assistant:

- **Sensors**: CPU temp per core, CPU load, memory usage, disk usage, network stats
- **Switches/Buttons**: VM control, firewall management, WiFi AP control
- **Diagnostic**: System updates, SMART disk status, connected devices, PPPoE credentials

All entities are linked to a single device in HA with:
- Device ID: `nivuus`
- Name: `Nivuus`
- Model: `System Agent v1.0`

## Infrastructure Context

The Nivuus server runs:
- **Host OS**: Debian 12 (Bookworm)
- **CPU**: Intel i9-12900K (8 P-cores + 8 E-cores)
- **GPU**: NVIDIA RTX 4070 (VFIO passthrough)
- **Hypervisor**: QEMU/KVM with libvirt
- **Network**: 3 bridges (localBridge, publicBridge, internalBridge), PPPoE connection
- **Firewall**: firewalld with multiple zones
- **WiFi**: Dual-band hostapd (2.4GHz + 5GHz)
- **Docker**: 22+ containers including Home Assistant, Mosquitto MQTT, Plex, etc.

See `docs/system-audit.md` for complete infrastructure documentation.

### WAN / PPPoE (Orange/Sosh fibre) — CRITICAL

The WAN is a PPPoE session over VLAN 835. **The physical WAN port is now `enp5s0` → VLAN `enp5s0.835`** (was historically `enp6s0.835`; the cable/port moved). NM still manages the VLAN `enp5s0.835` and brings it up at boot.

**Boot persistence is handled by NetworkManager** (profile `pppoe-enp6s0.835`, autoconnect=yes, zone=external):
- The **critical config** for PPPoE-over-VLAN with NM is to set **BOTH** `connection.interface-name=ppp0` (the ppp device NM creates) **AND** `pppoe.parent=enp5s0.835` (the VLAN). NM does support a VLAN parent (the earlier "RH bug 1663719 / unsupported" belief was wrong — the real cause was an *empty* `connection.interface-name`, which yields `error determine name for pppoe`; setting `interface-name` to the VLAN device instead yields `No suitable device found ... mismatching interface name`). Validated 2026-05-25.
- The HA `PppoeCredentials.ts` integration edits this nmconnection file for credentials; NM now actually brings up the link.
- **Fallback (kept, disabled):** systemd unit `/etc/systemd/system/pppoe-dsl.service` runs `pppd call dsl-provider persist holdoff 60 maxfail 0 nodetach` over peer file `/etc/ppp/peers/dsl-provider` (`pty "pppoe -I enp5s0.835 ..."`, `user "fti/CHANGE_ME"`, CHAP via `/etc/ppp/chap-secrets` + `/etc/ppp/pap-secrets`). If NM ever fails: `nmcli con down pppoe-enp6s0.835 && systemctl start pppoe-dsl.service`. Do NOT run both at once (they fight for the enp5s0.835 PPPoE session).

**Orange BNG reconnect cooldown (IMPORTANT):** after a clean pppd teardown (SIGTERM → PADT), Orange holds the session ~3-5 min and rejects fast reconnects (CHAP fails even with the right password). **Never hammer reconnects** — that is why the unit uses `RestartSec=120` + pppd `holdoff 60` + `persist` (persist redials without a clean PADT). When recovering manually after a kill, wait ~5 min before relaunching.

**Firewalld zone for ppp0:** `ppp0` is dynamic and must be placed in the `external` zone, done by `/etc/ppp/ip-up.d/firewalld-external` on every link-up. Without it, ppp0 falls into the default `internal` zone (too permissive for WAN) AND the external-zone forward-ports (cloud-gaming → 192.168.3.2) don't apply. firewalld uses the **nftables** backend (`table inet firewalld`) — `iptables -t nat -S` looks empty but isn't; check `nft list table inet firewalld`. `net.ipv4.ip_forward` is already persistent in `/etc/sysctl.conf`.

**Recovery if internet is down at boot:** `sudo nmcli connection up pppoe-enp6s0.835` (after a ~5 min wait if Orange is in cooldown). Last-resort fallback: `sudo systemctl start pppoe-dsl.service` (disable NM autoconnect first to avoid a fight: `nmcli con modify pppoe-enp6s0.835 connection.autoconnect no`). The bridges/WiFi (localBridge/publicBridge/internalBridge) are NM-managed and rebuild cleanly on a full reboot — a NM *restart* (not reboot) can orphan localBridge's members (hostapd wlp10s0/wlp11s0 + enp14s0), breaking home WiFi; a reboot fixes it.

## File Structure Key Points

```
mqtt/
├── src/
│   ├── core/              # Agent, BaseFeature, types
│   ├── features/          # All monitoring features (cpu, memory, disk, etc.)
│   ├── mqtt/              # MQTT client wrapper
│   ├── utils/             # Utilities (logger, exec, MAC vendor lookup)
│   ├── homeassistant/     # HA discovery services
│   ├── cli/               # CLI tools for sending alerts/events
│   └── config.ts          # Configuration manager (CRITICAL: maintains entity consistency)
├── config/
│   └── agent.yaml         # Main configuration file
├── dist/                  # Compiled JavaScript output
└── bin/                   # Executable wrapper
```

## Critical Implementation Notes

1. **Entity Consistency**: The `device_info.identifiers` must remain consistent between normal and error configurations to prevent duplicate Home Assistant entities

2. **Feature Registration**: Features must be added to `availableFeatures` map in `Agent.ts` to be discoverable

3. **Topic Prefixing**: BaseFeature automatically prefixes topics with `{base_topic}/{device_id}/` - don't manually add this prefix in features

4. **Discovery Publishing**: Features publish discovery messages to `homeassistant/{component}/{device_id}/{unique_id}/config` with retain flag

5. **State vs Attributes**: Use separate topics for state (single value) and attributes (JSON object with additional data)

6. **Entity Naming Convention (CRITICAL)**:
   - **NEVER** include `${this.deviceInfo.name}` or `${baseName}` with device name in entity `name` field
   - Home Assistant automatically prepends the device name from `device.name` when generating `entity_id`
   - Adding device name manually creates duplicate prefixes like `sensor.nivuus_nivuus_cpu_temperature`
   - **Correct format**: `{Category} {Name} {Type}` (e.g., `"CPU Temperature"`, `"Network localBridge Device Count"`)
   - **Wrong format**: `${this.deviceInfo.name} {Category} {Name}` (creates "Nivuus Nivuus CPU Temperature")
   - Category prefixes to use: "CPU", "Memory", "Disk", "Network", "VM", "System", "Security", "Motherboard"
   - Always include descriptive type suffix: "Sensor", "Button", "Switch", etc.

7. **Glances Conflict (RESOLVED)**: There was previously an external Glances process publishing to MQTT that created 162 duplicate entities (sensor.glances_nivuus_*). This process has been stopped and entities removed. The mqtt-system-agent now handles all monitoring.

8. **MQTT Retained Message Cleanup**: When changing entity naming, use `clean_mqtt_retained.py` to clear all old discovery messages before restarting the service to avoid entity duplication in Home Assistant

## Feature-Specific Implementation Details

### WiFi/Hostapd Management (`mqtt/src/features/wifi/HostapdManager.ts`)

**Key Features:**
- **Per-network configuration**: Each WiFi network (SSID) gets its own set of 6 entities:
  - Text inputs for SSID name and password (mode: text for visibility)
  - Select dropdown for security type (WPA2-PSK, WPA3-SAE, WPA2/WPA3-Mixed, Open)
  - Apply and Delete buttons
  - Status sensor showing active bands (2.4GHz, 5GHz, or both)
- **Numeric network IDs**: Uses `network_1`, `network_2`, etc. instead of sanitized SSID names to avoid special character issues
- **Dual-band merging**: Networks with same SSID in both 2.4GHz and 5GHz configs are merged into single entity set
- **Config file preservation**: All hostapd parameters (bridge, interface, access_network_type) are preserved when updating networks
- **Security type mapping**: Complete mapping from HA select options to hostapd config parameters (wpa, wpa_key_mgmt, rsn_pairwise, etc.)

**Critical Implementation Points:**
- Password inputs use `mode: 'text'` not `mode: 'password'` for editability
- Entity IDs use numeric counter (1, 2, 3...) to avoid special characters in SSID names
- Changes are applied atomically: backup → temp file → atomic move → reload hostapd
- Config paths: `/etc/hostapd/2.4Ghz.conf` and `/etc/hostapd/5Ghz.conf`

### PPPoE Credentials Management (`mqtt/src/features/network/PppoeCredentials.ts`)

**Key Features:**
- **NetworkManager integration**: Reads and writes credentials directly to `/etc/NetworkManager/system-connections/pppoe-enp6s0.835.nmconnection`
- **Real credential display**: Username and password are read from nmconnection file and displayed in Home Assistant
- **Connection restart**: Automatically reloads and restarts PPPoE connection after credential changes
- **No server field**: Previous "server" input was removed as it's not needed for PPPoE configuration

**Critical Implementation Points:**
- Password input uses `mode: 'text'` not `mode: 'password'` for editability
- Credentials are read with sudo due to nmconnection file permissions (600)
- INI-style parser for `[pppoe]` section: `username=` and `password=` lines
- After saving: `nmcli connection reload` + `nmcli connection down/up pppoe-enp6s0.835`
- Backup created before any modification: `{path}.backup`

**Legacy files not used:**
- `/etc/ppp/chap-secrets` and `/etc/ppp/pap-secrets` - monitored but not modified
- NetworkManager is the single source of truth for active PPPoE configuration

### Firewall Management (`mqtt/src/features/firewall/FirewallManager.ts`)

**Key Features:**
- **Per-interface zone selection**: Each network interface (including bridges) gets a dropdown to change its firewall zone
- **Port forward management**: Full CRUD interface for port forwarding rules with 5 inputs:
  - Source port, destination IP, destination port, protocol (tcp/udp), zone
  - Add and Remove buttons execute firewall-cmd commands
- **Zone detail sensors**: For each active zone, displays:
  - Port forwards count + detailed list (port→toaddr:toport)
  - Services count + list
  - Open ports count + list
  - Masquerading status (binary sensor ON/OFF)
- **All interfaces included**: Pattern `relevantInterfacePatterns` OR `iface.includes('Bridge')` captures:
  - Standard interfaces: enp6s0.835, ppp0, enp15s0, enp14s0
  - Bridges: localBridge, internalBridge, publicBridge

**Critical Implementation Points:**
- Interface zone changes are atomic: remove from old zone → add to new zone → reload
- All changes use `--permanent` flag + `firewall-cmd --reload`
- Port forward format: `port=X:proto=Y:toport=Z:toaddr=A`
- Zone details updated every 5 minutes in `update()` cycle
- Empty string states published for all inputs to avoid "unknown" values
- Bridge detection: `iface.includes('Bridge')` catches localBridge, internalBridge, publicBridge

**Active Zones (Current Configuration):**
- **docker**: 5 interfaces, masquerade enabled, 7 port forwards to 192.168.3.2
- **external**: enp6s0.835 + ppp0, masquerade enabled, target REJECT, exposed services
- **home**: localBridge, target ACCEPT, 26 services, no masquerade
- **internal**: enp15s0 + internalBridge + vnet17 + enp14s0, 11 services
- **public**: publicBridge, masquerade enabled, target REJECT

### Common Patterns Across Features

**Input entity initialization:**
- Always publish empty string `''` states for text inputs to avoid "unknown" in Home Assistant
- Publish states AFTER publishing discovery entities
- Use `mode: 'text'` for password fields when editability is required

**MQTT message handling:**
- Store pending changes in memory until "Apply" button is pressed
- Echo back state changes immediately for UI responsiveness
- Use atomic file operations: backup → temp → move → reload service

**Error handling:**
- Publish error messages to `{feature_name}/last_action/state` sensor
- Log errors with logger.error() for debugging
- Validate inputs before executing system commands

## Related Documentation

- **Main README**: `/README.md` - Project overview and installation
- **System Audit**: `/docs/system-audit.md` - Complete infrastructure documentation
- **Network Config**: `/configs/network/` - NetworkManager and hostapd setup
- **Firewall Config**: `/configs/firewall/` - firewalld and nftables rules
- **VM Config**: `/docs/vm-configuration.md` - QEMU/KVM setup with GPU passthrough
