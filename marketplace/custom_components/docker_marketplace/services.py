"""Services for Docker Marketplace integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall

from .const import ATTR_APP_ID, ATTR_CONFIG, ATTR_REMOVE_DATA, DOMAIN
from .coordinator import DockerMarketplaceCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_install_app(
    hass: HomeAssistant,
    coordinator: DockerMarketplaceCoordinator,
    call: ServiceCall,
) -> None:
    """Handle install_app service call."""
    app_id = call.data[ATTR_APP_ID]
    config = call.data.get(ATTR_CONFIG, {})

    _LOGGER.info("Service call: install_app %s", app_id)

    success = await coordinator.install_app(app_id, config)

    if success:
        hass.bus.async_fire(
            f"{DOMAIN}_app_installed",
            {"app_id": app_id},
        )
    else:
        _LOGGER.error("Failed to install app %s", app_id)


async def async_remove_app(
    hass: HomeAssistant,
    coordinator: DockerMarketplaceCoordinator,
    call: ServiceCall,
) -> None:
    """Handle remove_app service call."""
    app_id = call.data[ATTR_APP_ID]
    remove_data = call.data.get(ATTR_REMOVE_DATA, False)

    _LOGGER.info("Service call: remove_app %s (remove_data=%s)", app_id, remove_data)

    success = await coordinator.remove_app(app_id, remove_data)

    if success:
        hass.bus.async_fire(
            f"{DOMAIN}_app_removed",
            {"app_id": app_id},
        )
    else:
        _LOGGER.error("Failed to remove app %s", app_id)


async def async_update_app(
    hass: HomeAssistant,
    coordinator: DockerMarketplaceCoordinator,
    call: ServiceCall,
) -> None:
    """Handle update_app service call."""
    app_id = call.data[ATTR_APP_ID]

    _LOGGER.info("Service call: update_app %s", app_id)

    success = await coordinator.update_app(app_id)

    if success:
        hass.bus.async_fire(
            f"{DOMAIN}_app_updated",
            {"app_id": app_id},
        )
    else:
        _LOGGER.error("Failed to update app %s", app_id)


async def async_start_app(
    hass: HomeAssistant,
    coordinator: DockerMarketplaceCoordinator,
    call: ServiceCall,
) -> None:
    """Handle start_app service call."""
    app_id = call.data[ATTR_APP_ID]

    _LOGGER.info("Service call: start_app %s", app_id)

    success = await coordinator.start_app(app_id)

    if not success:
        _LOGGER.error("Failed to start app %s", app_id)


async def async_stop_app(
    hass: HomeAssistant,
    coordinator: DockerMarketplaceCoordinator,
    call: ServiceCall,
) -> None:
    """Handle stop_app service call."""
    app_id = call.data[ATTR_APP_ID]

    _LOGGER.info("Service call: stop_app %s", app_id)

    success = await coordinator.stop_app(app_id)

    if not success:
        _LOGGER.error("Failed to stop app %s", app_id)


async def async_restart_app(
    hass: HomeAssistant,
    coordinator: DockerMarketplaceCoordinator,
    call: ServiceCall,
) -> None:
    """Handle restart_app service call."""
    app_id = call.data[ATTR_APP_ID]

    _LOGGER.info("Service call: restart_app %s", app_id)

    success = await coordinator.restart_app(app_id)

    if not success:
        _LOGGER.error("Failed to restart app %s", app_id)
