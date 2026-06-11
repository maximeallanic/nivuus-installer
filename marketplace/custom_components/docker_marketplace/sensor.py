"""Sensor platform for Docker Marketplace."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfInformation
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, STATE_NOT_INSTALLED
from .coordinator import DockerMarketplaceCoordinator, InstalledApp

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Docker Marketplace sensors."""
    coordinator: DockerMarketplaceCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    # Track which app_ids already have entities
    tracked_app_ids: set[str] = set()

    @callback
    def async_add_sensors() -> None:
        """Add sensors for newly installed apps."""
        if not coordinator.data:
            return

        new_entities = []
        for app_id in coordinator.data.installed_apps:
            if app_id not in tracked_app_ids:
                tracked_app_ids.add(app_id)
                new_entities.extend(
                    [
                        AppStatusSensor(coordinator, app_id),
                        AppCpuSensor(coordinator, app_id),
                        AppMemorySensor(coordinator, app_id),
                    ]
                )

        if new_entities:
            async_add_entities(new_entities)

    # Add initial entities
    if coordinator.data:
        entities = []
        for app_id in coordinator.data.installed_apps:
            tracked_app_ids.add(app_id)
            entities.extend(
                [
                    AppStatusSensor(coordinator, app_id),
                    AppCpuSensor(coordinator, app_id),
                    AppMemorySensor(coordinator, app_id),
                ]
            )
        async_add_entities(entities)

    # Listen for coordinator updates to add new entities
    coordinator.async_add_listener(async_add_sensors)


class AppBaseSensor(CoordinatorEntity[DockerMarketplaceCoordinator], SensorEntity):
    """Base sensor for Docker Marketplace apps."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.app_id = app_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, app_id)},
            name=self._get_app_name(),
            manufacturer="Docker Marketplace",
            model="Container",
        )

    def _get_app_name(self) -> str:
        """Get app name from catalog or installed apps."""
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


class AppStatusSensor(AppBaseSensor):
    """Sensor for app status."""

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize status sensor."""
        super().__init__(coordinator, app_id)
        self._attr_unique_id = f"{DOMAIN}_{app_id}_status"
        self._attr_name = "Status"
        self._attr_icon = "mdi:docker"

    @property
    def native_value(self) -> str:
        """Return the status."""
        app = self._get_installed_app()
        if app:
            return app.state
        return STATE_NOT_INSTALLED

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        app = self._get_installed_app()
        if app:
            return {
                "container_name": app.container_name,
                "image": app.image,
                "version": app.version,
            }
        return {}


class AppCpuSensor(AppBaseSensor):
    """Sensor for app CPU usage."""

    _attr_device_class = SensorDeviceClass.POWER_FACTOR
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize CPU sensor."""
        super().__init__(coordinator, app_id)
        self._attr_unique_id = f"{DOMAIN}_{app_id}_cpu"
        self._attr_name = "CPU Usage"
        self._attr_icon = "mdi:cpu-64-bit"

    @property
    def native_value(self) -> float | None:
        """Return CPU usage."""
        app = self._get_installed_app()
        if app and app.state == "running":
            return app.cpu_percent
        return None


class AppMemorySensor(AppBaseSensor):
    """Sensor for app memory usage."""

    _attr_device_class = SensorDeviceClass.DATA_SIZE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfInformation.MEGABYTES

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize memory sensor."""
        super().__init__(coordinator, app_id)
        self._attr_unique_id = f"{DOMAIN}_{app_id}_memory"
        self._attr_name = "Memory Usage"
        self._attr_icon = "mdi:memory"

    @property
    def native_value(self) -> float | None:
        """Return memory usage in MB."""
        app = self._get_installed_app()
        if app and app.state == "running":
            return round(app.memory_usage / (1024 * 1024), 1)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional memory attributes."""
        app = self._get_installed_app()
        if app and app.state == "running":
            return {
                "memory_percent": app.memory_percent,
            }
        return {}
