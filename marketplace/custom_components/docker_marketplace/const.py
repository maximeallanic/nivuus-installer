"""Constants for Docker Marketplace integration."""
from typing import Final

DOMAIN: Final = "docker_marketplace"
NAME: Final = "Docker Marketplace"
VERSION: Final = "1.0.0"

# Configuration keys
CONF_DOCKER_HOST: Final = "docker_host"
CONF_CATALOG_PATH: Final = "catalog_path"
CONF_STACKS_PATH: Final = "stacks_path"

# Default values
DEFAULT_DOCKER_HOST: Final = "unix:///var/run/docker.sock"
DEFAULT_CATALOG_PATH: Final = "/config/catalog"
DEFAULT_STACKS_PATH: Final = "/config/stacks"
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds

# Container states
STATE_RUNNING: Final = "running"
STATE_STOPPED: Final = "stopped"
STATE_NOT_INSTALLED: Final = "not_installed"
STATE_INSTALLING: Final = "installing"
STATE_ERROR: Final = "error"

# Services
SERVICE_INSTALL_APP: Final = "install_app"
SERVICE_REMOVE_APP: Final = "remove_app"
SERVICE_UPDATE_APP: Final = "update_app"
SERVICE_START_APP: Final = "start_app"
SERVICE_STOP_APP: Final = "stop_app"
SERVICE_RESTART_APP: Final = "restart_app"

# Attributes
ATTR_APP_ID: Final = "app_id"
ATTR_CONFIG: Final = "config"
ATTR_REMOVE_DATA: Final = "remove_data"
ATTR_CATEGORY: Final = "category"
ATTR_CONTAINER_ID: Final = "container_id"
ATTR_IMAGE: Final = "image"
ATTR_PORTS: Final = "ports"
ATTR_VOLUMES: Final = "volumes"
ATTR_CPU_USAGE: Final = "cpu_usage"
ATTR_MEMORY_USAGE: Final = "memory_usage"

# Events
EVENT_APP_INSTALLED: Final = f"{DOMAIN}_app_installed"
EVENT_APP_REMOVED: Final = f"{DOMAIN}_app_removed"
EVENT_APP_UPDATED: Final = f"{DOMAIN}_app_updated"

# WebSocket commands
WS_TYPE_CATALOG: Final = f"{DOMAIN}/catalog"
WS_TYPE_INSTALLED: Final = f"{DOMAIN}/installed"
WS_TYPE_INSTALL: Final = f"{DOMAIN}/install"
WS_TYPE_REMOVE: Final = f"{DOMAIN}/remove"
WS_TYPE_START: Final = f"{DOMAIN}/start"
WS_TYPE_STOP: Final = f"{DOMAIN}/stop"
WS_TYPE_RESTART: Final = f"{DOMAIN}/restart"
WS_TYPE_LOGS: Final = f"{DOMAIN}/logs"
WS_TYPE_APP_STATUS: Final = f"{DOMAIN}/app_status"
WS_TYPE_GET_CONFIG: Final = f"{DOMAIN}/get_config"
WS_TYPE_UPDATE_CONFIG: Final = f"{DOMAIN}/update_config"

# Categories
CATEGORY_MEDIA: Final = "media"
CATEGORY_GAMING: Final = "gaming"
CATEGORY_DOWNLOAD: Final = "download"
CATEGORY_SMART_HOME: Final = "smart_home"
CATEGORY_SECURITY: Final = "security"
CATEGORY_NETWORK: Final = "network"
CATEGORY_AI: Final = "ai"
CATEGORY_MONITORING: Final = "monitoring"
CATEGORY_BACKUP: Final = "backup"
CATEGORY_WEB: Final = "web"

CATEGORIES: Final = [
    CATEGORY_MEDIA,
    CATEGORY_GAMING,
    CATEGORY_DOWNLOAD,
    CATEGORY_SMART_HOME,
    CATEGORY_SECURITY,
    CATEGORY_NETWORK,
    CATEGORY_AI,
    CATEGORY_MONITORING,
    CATEGORY_BACKUP,
    CATEGORY_WEB,
]

# Icons per category
CATEGORY_ICONS: Final = {
    CATEGORY_MEDIA: "mdi:play-circle",
    CATEGORY_GAMING: "mdi:gamepad-variant",
    CATEGORY_DOWNLOAD: "mdi:download",
    CATEGORY_SMART_HOME: "mdi:home-automation",
    CATEGORY_SECURITY: "mdi:shield-lock",
    CATEGORY_NETWORK: "mdi:network",
    CATEGORY_AI: "mdi:robot",
    CATEGORY_MONITORING: "mdi:chart-line",
    CATEGORY_BACKUP: "mdi:backup-restore",
    CATEGORY_WEB: "mdi:web",
}

# Platforms
PLATFORMS: Final = ["sensor", "button", "switch", "update"]

# Update check interval (seconds)
UPDATE_CHECK_INTERVAL: Final = 21600  # 6 hours
