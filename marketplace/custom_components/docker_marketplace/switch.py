"""Switch platform for Docker Marketplace."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATE_RUNNING, STATE_STOPPED
from .coordinator import DockerMarketplaceCoordinator, InstalledApp

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Docker Marketplace switches."""
    coordinator: DockerMarketplaceCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    # Track which app_ids already have entities
    tracked_app_ids: set[str] = set()

    @callback
    def async_add_switches() -> None:
        """Add switches for newly installed apps."""
        if not coordinator.data:
            return

        new_entities = []
        for app_id in coordinator.data.installed_apps:
            if app_id not in tracked_app_ids:
                tracked_app_ids.add(app_id)
                new_entities.append(AppPowerSwitch(coordinator, app_id))

        if new_entities:
            async_add_entities(new_entities)

    # Add initial entities
    if coordinator.data:
        entities = []
        for app_id in coordinator.data.installed_apps:
            tracked_app_ids.add(app_id)
            entities.append(AppPowerSwitch(coordinator, app_id))
        async_add_entities(entities)

    # Listen for coordinator updates
    coordinator.async_add_listener(async_add_switches)


class AppPowerSwitch(CoordinatorEntity[DockerMarketplaceCoordinator], SwitchEntity):
    """Switch to control app running state."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.app_id = app_id
        self._attr_unique_id = f"{DOMAIN}_{app_id}_power"
        self._attr_name = "Running"
        self._attr_icon = "mdi:power"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, app_id)},
            name=self._get_app_name(),
            manufacturer="Docker Marketplace",
            model="Container",
        )

    def _get_app_name(self) -> str:
        """Get app name."""
        if self.coordinator.data:
            app = self.coordinator.data.installed_apps.get(self.app_id)
            if app:
                return app.name
        return self.app_id

    def _get_installed_app(self) -> InstalledApp | None:
        """Get installed app data."""
        if self.coordinator.data:
            return self.coordinator.data.installed_apps.get(self.app_id)
        return None

    @property
    def is_on(self) -> bool:
        """Return true if app is running."""
        app = self._get_installed_app()
        return app is not None and app.state == STATE_RUNNING

    @property
    def available(self) -> bool:
        """Return if switch is available."""
        app = self._get_installed_app()
        return app is not None and app.state in (STATE_RUNNING, STATE_STOPPED)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on (start) the app."""
        _LOGGER.info("Starting app %s via switch", self.app_id)
        await self.coordinator.start_app(self.app_id)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off (stop) the app."""
        _LOGGER.info("Stopping app %s via switch", self.app_id)
        await self.coordinator.stop_app(self.app_id)
