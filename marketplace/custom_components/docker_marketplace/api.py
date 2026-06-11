"""WebSocket API for Docker Marketplace frontend."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    WS_TYPE_APP_STATUS,
    WS_TYPE_CATALOG,
    WS_TYPE_GET_CONFIG,
    WS_TYPE_INSTALL,
    WS_TYPE_INSTALLED,
    WS_TYPE_LOGS,
    WS_TYPE_REMOVE,
    WS_TYPE_RESTART,
    WS_TYPE_START,
    WS_TYPE_STOP,
    WS_TYPE_UPDATE_CONFIG,
)

_LOGGER = logging.getLogger(__name__)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_CATALOG,
    }
)
@websocket_api.async_response
async def websocket_get_catalog(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the full app catalog."""
    catalog = hass.data[DOMAIN].get("catalog")

    if not catalog:
        connection.send_error(msg["id"], "not_found", "Catalog not loaded")
        return

    connection.send_result(msg["id"], catalog.to_dict())


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_INSTALLED,
    }
)
@websocket_api.async_response
async def websocket_get_installed(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return installed apps with status."""
    coordinator = hass.data[DOMAIN].get("coordinator")

    if not coordinator or not coordinator.data:
        connection.send_result(msg["id"], {"apps": []})
        return

    apps = []
    for app_id, app in coordinator.data.installed_apps.items():
        apps.append(
            {
                "id": app.app_id,
                "name": app.name,
                "state": app.state,
                "image": app.image,
                "version": app.version,
                "cpu_percent": app.cpu_percent,
                "memory_usage": app.memory_usage,
                "memory_percent": app.memory_percent,
            }
        )

    connection.send_result(msg["id"], {"apps": apps})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_INSTALL,
        vol.Required("app_id"): str,
        vol.Optional("config"): dict,
    }
)
@websocket_api.async_response
async def websocket_install_app(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Install an app from the catalog."""
    coordinator = hass.data[DOMAIN].get("coordinator")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]
    config = msg.get("config", {})

    _LOGGER.info("WebSocket: Installing app %s", app_id)

    # Send initial progress
    connection.send_message(
        websocket_api.messages.event_message(
            msg["id"],
            {"status": "installing", "app_id": app_id, "progress": 0},
        )
    )

    success = await coordinator.install_app(app_id, config)

    if success:
        connection.send_result(
            msg["id"],
            {"status": "success", "app_id": app_id},
        )
    else:
        connection.send_error(
            msg["id"],
            "install_failed",
            f"Failed to install {app_id}",
        )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_REMOVE,
        vol.Required("app_id"): str,
        vol.Optional("remove_data", default=False): bool,
    }
)
@websocket_api.async_response
async def websocket_remove_app(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove an installed app."""
    coordinator = hass.data[DOMAIN].get("coordinator")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]
    remove_data = msg.get("remove_data", False)

    _LOGGER.info("WebSocket: Removing app %s", app_id)

    success = await coordinator.remove_app(app_id, remove_data)

    if success:
        connection.send_result(
            msg["id"],
            {"status": "success", "app_id": app_id},
        )
    else:
        connection.send_error(
            msg["id"],
            "remove_failed",
            f"Failed to remove {app_id}",
        )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_LOGS,
        vol.Required("app_id"): str,
        vol.Optional("tail", default=100): int,
    }
)
@websocket_api.async_response
async def websocket_get_logs(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Get logs for an app."""
    coordinator = hass.data[DOMAIN].get("coordinator")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]
    tail = msg.get("tail", 100)

    logs = await coordinator.get_logs(app_id, tail)

    if logs is not None:
        connection.send_result(
            msg["id"],
            {"app_id": app_id, "logs": logs},
        )
    else:
        connection.send_error(
            msg["id"],
            "logs_unavailable",
            f"Cannot get logs for {app_id}",
        )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_APP_STATUS,
        vol.Required("app_id"): str,
    }
)
@websocket_api.async_response
async def websocket_get_app_status(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Get detailed status for an app."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    catalog = hass.data[DOMAIN].get("catalog")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]

    # Get catalog info
    app_info = catalog.app_to_dict(app_id) if catalog else None

    # Get installed info
    installed_app = coordinator.get_installed_app(app_id)

    result = {
        "app_id": app_id,
        "catalog": app_info,
        "installed": installed_app is not None,
    }

    if installed_app:
        result["status"] = {
            "state": installed_app.state,
            "image": installed_app.image,
            "version": installed_app.version,
            "cpu_percent": installed_app.cpu_percent,
            "memory_usage": installed_app.memory_usage,
            "memory_percent": installed_app.memory_percent,
        }

    connection.send_result(msg["id"], result)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_START,
        vol.Required("app_id"): str,
    }
)
@websocket_api.async_response
async def websocket_start_app(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Start an installed app."""
    coordinator = hass.data[DOMAIN].get("coordinator")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]
    _LOGGER.info("WebSocket: Starting app %s", app_id)

    success = await coordinator.start_app(app_id)

    if success:
        connection.send_result(msg["id"], {"status": "success", "app_id": app_id})
    else:
        connection.send_error(msg["id"], "start_failed", f"Failed to start {app_id}")


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_STOP,
        vol.Required("app_id"): str,
    }
)
@websocket_api.async_response
async def websocket_stop_app(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Stop an installed app."""
    coordinator = hass.data[DOMAIN].get("coordinator")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]
    _LOGGER.info("WebSocket: Stopping app %s", app_id)

    success = await coordinator.stop_app(app_id)

    if success:
        connection.send_result(msg["id"], {"status": "success", "app_id": app_id})
    else:
        connection.send_error(msg["id"], "stop_failed", f"Failed to stop {app_id}")


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_RESTART,
        vol.Required("app_id"): str,
    }
)
@websocket_api.async_response
async def websocket_restart_app(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Restart an installed app."""
    coordinator = hass.data[DOMAIN].get("coordinator")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]
    _LOGGER.info("WebSocket: Restarting app %s", app_id)

    success = await coordinator.restart_app(app_id)

    if success:
        connection.send_result(msg["id"], {"status": "success", "app_id": app_id})
    else:
        connection.send_error(msg["id"], "restart_failed", f"Failed to restart {app_id}")


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_GET_CONFIG,
        vol.Required("app_id"): str,
    }
)
@websocket_api.async_response
async def websocket_get_config(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Get configuration for an installed app."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    catalog = hass.data[DOMAIN].get("catalog")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]

    # Get saved config
    config = await coordinator.get_app_config(app_id)

    # Get app definition for schema info
    app_def = catalog.get_app(app_id) if catalog else None

    result = {
        "app_id": app_id,
        "config": config or {},
        "schema": None,
    }

    # Include schema info from catalog
    if app_def:
        schema = {
            "ports": [],
            "volumes": [],
            "environment": [],
        }

        if app_def.ports:
            for port in app_def.ports:
                schema["ports"].append({
                    "key": f"port_{port.container}",
                    "container": port.container,
                    "host": port.host,
                    "protocol": port.protocol,
                    "description": port.description,
                })

        if app_def.volumes:
            for vol in app_def.volumes:
                schema["volumes"].append({
                    "key": f"volume_{vol.name}",
                    "name": vol.name,
                    "container": vol.container,
                    "default_host": vol.default_host,
                    "description": vol.description,
                    "required": vol.required,
                })

        if app_def.environment:
            for env in app_def.environment:
                schema["environment"].append({
                    "key": f"env_{env.name}",
                    "name": env.name,
                    "default": env.default,
                    "description": env.description,
                    "required": env.required,
                    "secret": env.secret,
                })

        result["schema"] = schema

    connection.send_result(msg["id"], result)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_UPDATE_CONFIG,
        vol.Required("app_id"): str,
        vol.Required("config"): dict,
    }
)
@websocket_api.async_response
async def websocket_update_config(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update configuration for an installed app."""
    coordinator = hass.data[DOMAIN].get("coordinator")

    if not coordinator:
        connection.send_error(msg["id"], "not_ready", "Coordinator not ready")
        return

    app_id = msg["app_id"]
    config = msg["config"]

    _LOGGER.info("WebSocket: Updating config for app %s", app_id)

    success = await coordinator.update_config(app_id, config)

    if success:
        connection.send_result(msg["id"], {
            "status": "success",
            "app_id": app_id,
            "message": "Configuration updated. Restart the app to apply changes.",
        })
    else:
        connection.send_error(msg["id"], "update_failed", f"Failed to update config for {app_id}")
