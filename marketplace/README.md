# Docker Marketplace for Home Assistant

A Home Assistant custom integration that provides a marketplace for installing and managing Docker containers directly from the HA interface.

## Features

- **Browse Apps** - Curated catalog of Docker applications organized by category
- **One-Click Install** - Install apps with sensible defaults
- **Container Management** - Start, stop, restart, update, and remove containers
- **Resource Monitoring** - CPU and memory usage sensors for each app
- **WebSocket API** - Real-time communication with custom frontend panel
- **HACS Compatible** - Easy installation via Home Assistant Community Store

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/nivuus/ha-docker-marketplace` with category "Integration"
5. Search for "Docker Marketplace" and install
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/docker_marketplace` folder to your `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Settings > Devices & Services > Add Integration
4. Search for "Docker Marketplace"

## Configuration

During setup, you'll need to provide:

| Option | Default | Description |
|--------|---------|-------------|
| Docker Host | `unix:///var/run/docker.sock` | Docker socket or TCP address |
| Catalog Path | `/opt/nivuus/marketplace/catalog` | Path to the app catalog |
| Stacks Path | `/opt/nivuus/stacks` | Where installed apps are stored |

## Usage

### Services

| Service | Description |
|---------|-------------|
| `docker_marketplace.install_app` | Install an app from the catalog |
| `docker_marketplace.remove_app` | Remove an installed app |
| `docker_marketplace.update_app` | Update an installed app |
| `docker_marketplace.start_app` | Start an installed app |
| `docker_marketplace.stop_app` | Stop a running app |
| `docker_marketplace.restart_app` | Restart an app |

### Entities

For each installed app, the following entities are created:

- `sensor.docker_{app}_status` - Container status (running/stopped)
- `sensor.docker_{app}_cpu` - CPU usage percentage
- `sensor.docker_{app}_memory` - Memory usage in MB
- `button.docker_{app}_start` - Start button
- `button.docker_{app}_stop` - Stop button
- `button.docker_{app}_restart` - Restart button
- `button.docker_{app}_update` - Update button
- `button.docker_{app}_remove` - Remove button
- `switch.docker_{app}_power` - On/Off switch

### WebSocket API

For frontend development:

```javascript
// Get catalog
hass.connection.sendMessagePromise({
  type: "docker_marketplace/catalog"
});

// Get installed apps
hass.connection.sendMessagePromise({
  type: "docker_marketplace/installed"
});

// Install an app
hass.connection.sendMessagePromise({
  type: "docker_marketplace/install",
  app_id: "plex",
  config: {}
});

// Get logs
hass.connection.sendMessagePromise({
  type: "docker_marketplace/logs",
  app_id: "plex",
  tail: 100
});
```

## Adding Apps to the Catalog

Create a YAML file in `catalog/apps/`:

```yaml
id: myapp
name: My Application
category: media
description: Description of the application
icon: mdi:docker
version: "1.0"

ports:
  - container: 8080
    host: 8080
    protocol: tcp
    description: Web interface

volumes:
  - name: config
    container: /config
    description: Configuration directory

environment:
  - name: TZ
    default: "Europe/Paris"
    description: Timezone

compose:
  image: myapp/myapp:latest
  restart: unless-stopped
```

## Development

### Project Structure

```
marketplace/
├── custom_components/docker_marketplace/
│   ├── __init__.py          # Integration setup
│   ├── manifest.json         # Integration metadata
│   ├── config_flow.py        # Configuration UI
│   ├── coordinator.py        # Data coordinator
│   ├── docker_client.py      # Docker SDK wrapper
│   ├── catalog.py            # Catalog management
│   ├── sensor.py             # Sensor entities
│   ├── button.py             # Button entities
│   ├── switch.py             # Switch entities
│   ├── services.py           # Service handlers
│   └── api.py                # WebSocket API
├── catalog/
│   ├── catalog.yaml          # Category definitions
│   └── apps/                 # App definitions
└── frontend/                 # Custom panel (WIP)
```

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.
