"""Update platform for Docker Marketplace."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DockerMarketplaceCoordinator, InstalledApp

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Docker Marketplace update entities."""
    coordinator: DockerMarketplaceCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    # Track which app_ids already have entities
    tracked_app_ids: set[str] = set()

    @callback
    def async_add_updates() -> None:
        """Add update entities for newly installed apps."""
        if not coordinator.data:
            return

        new_entities = []
        for app_id in coordinator.data.installed_apps:
            if app_id not in tracked_app_ids:
                tracked_app_ids.add(app_id)
                new_entities.append(AppUpdateEntity(coordinator, app_id))

        if new_entities:
            async_add_entities(new_entities)

    # Add initial entities
    if coordinator.data:
        entities = []
        for app_id in coordinator.data.installed_apps:
            tracked_app_ids.add(app_id)
            entities.append(AppUpdateEntity(coordinator, app_id))
        async_add_entities(entities)

    # Listen for coordinator updates to add new entities
    coordinator.async_add_listener(async_add_updates)


class AppUpdateEntity(CoordinatorEntity[DockerMarketplaceCoordinator], UpdateEntity):
    """Update entity for Docker Marketplace apps."""

    _attr_has_entity_name = True
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = (
        UpdateEntityFeature.INSTALL
        | UpdateEntityFeature.PROGRESS
    )

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize the update entity."""
        super().__init__(coordinator)
        self._app_id = app_id
        self._attr_unique_id = f"{DOMAIN}_{app_id}_update"
        self._attr_name = "Update"
        self._updating = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, app_id)},
            name=self._get_app_name(),
            manufacturer="Docker Marketplace",
            model="Container",
        )

    def _get_app_name(self) -> str:
        """Get app name from catalog or installed apps."""
        if self.coordinator.data:
            app = self.coordinator.data.installed_apps.get(self._app_id)
            if app:
                return app.name
        return self._app_id

    def _get_installed_app(self) -> InstalledApp | None:
        """Get installed app data."""
        if self.coordinator.data:
            return self.coordinator.data.installed_apps.get(self._app_id)
        return None

    @property
    def installed_version(self) -> str | None:
        """Return current installed version."""
        app = self._get_installed_app()
        if not app:
            return None

        # Use digest if available, otherwise use version from catalog
        if app.local_digest:
            return app.local_digest[:12]
        return app.version

    @property
    def latest_version(self) -> str | None:
        """Return latest available version."""
        app = self._get_installed_app()
        if not app:
            return None

        # Use remote digest if available
        if app.remote_digest:
            return app.remote_digest[:12]

        # If no remote digest, return installed version (no update available)
        if app.local_digest:
            return app.local_digest[:12]
        return app.version

    @property
    def in_progress(self) -> bool | int:
        """Return if update is in progress."""
        return self._updating

    @property
    def release_summary(self) -> str | None:
        """Return release summary."""
        app = self._get_installed_app()
        if not app:
            return None

        if app.update_available:
            return f"New Docker image available for {app.image}"
        return None

    @property
    def title(self) -> str | None:
        """Return title of the update."""
        app = self._get_installed_app()
        if app:
            return app.name
        return self._app_id

    @property
    def entity_picture(self) -> str | None:
        """Return entity picture."""
        # Could return app logo URL if available
        return None

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install the update."""
        self._updating = True
        self.async_write_ha_state()

        try:
            _LOGGER.info("Updating app %s", self._app_id)
            success = await self.coordinator.update_app(self._app_id)

            if success:
                _LOGGER.info("Successfully updated app %s", self._app_id)
                # Force update check to refresh digests
                await self.coordinator.force_update_check()
            else:
                _LOGGER.error("Failed to update app %s", self._app_id)

        finally:
            self._updating = False
            self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        app = self._get_installed_app()
        return app is not None
