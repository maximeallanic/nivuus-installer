"""Button platform for Docker Marketplace."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
    """Set up Docker Marketplace buttons."""
    coordinator: DockerMarketplaceCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    # Track which app_ids already have entities
    tracked_app_ids: set[str] = set()

    @callback
    def async_add_buttons() -> None:
        """Add buttons for newly installed apps."""
        if not coordinator.data:
            return

        new_entities = []
        for app_id in coordinator.data.installed_apps:
            if app_id not in tracked_app_ids:
                tracked_app_ids.add(app_id)
                new_entities.extend(
                    [
                        AppStartButton(coordinator, app_id),
                        AppStopButton(coordinator, app_id),
                        AppRestartButton(coordinator, app_id),
                        AppUpdateButton(coordinator, app_id),
                        AppRemoveButton(coordinator, app_id),
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
                    AppStartButton(coordinator, app_id),
                    AppStopButton(coordinator, app_id),
                    AppRestartButton(coordinator, app_id),
                    AppUpdateButton(coordinator, app_id),
                    AppRemoveButton(coordinator, app_id),
                ]
            )
        async_add_entities(entities)

    # Listen for coordinator updates
    coordinator.async_add_listener(async_add_buttons)


class AppBaseButton(CoordinatorEntity[DockerMarketplaceCoordinator], ButtonEntity):
    """Base button for Docker Marketplace apps."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.app_id = app_id
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


class AppStartButton(AppBaseButton):
    """Button to start an app."""

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize start button."""
        super().__init__(coordinator, app_id)
        self._attr_unique_id = f"{DOMAIN}_{app_id}_start"
        self._attr_name = "Start"
        self._attr_icon = "mdi:play"

    @property
    def available(self) -> bool:
        """Return if button is available."""
        app = self._get_installed_app()
        return app is not None and app.state == STATE_STOPPED

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Starting app %s", self.app_id)
        await self.coordinator.start_app(self.app_id)


class AppStopButton(AppBaseButton):
    """Button to stop an app."""

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize stop button."""
        super().__init__(coordinator, app_id)
        self._attr_unique_id = f"{DOMAIN}_{app_id}_stop"
        self._attr_name = "Stop"
        self._attr_icon = "mdi:stop"

    @property
    def available(self) -> bool:
        """Return if button is available."""
        app = self._get_installed_app()
        return app is not None and app.state == STATE_RUNNING

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Stopping app %s", self.app_id)
        await self.coordinator.stop_app(self.app_id)


class AppRestartButton(AppBaseButton):
    """Button to restart an app."""

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize restart button."""
        super().__init__(coordinator, app_id)
        self._attr_unique_id = f"{DOMAIN}_{app_id}_restart"
        self._attr_name = "Restart"
        self._attr_icon = "mdi:restart"

    @property
    def available(self) -> bool:
        """Return if button is available."""
        app = self._get_installed_app()
        return app is not None and app.state == STATE_RUNNING

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Restarting app %s", self.app_id)
        await self.coordinator.restart_app(self.app_id)


class AppUpdateButton(AppBaseButton):
    """Button to update an app."""

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize update button."""
        super().__init__(coordinator, app_id)
        self._attr_unique_id = f"{DOMAIN}_{app_id}_update"
        self._attr_name = "Update"
        self._attr_icon = "mdi:download"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Updating app %s", self.app_id)
        await self.coordinator.update_app(self.app_id)


class AppRemoveButton(AppBaseButton):
    """Button to remove an app."""

    def __init__(
        self,
        coordinator: DockerMarketplaceCoordinator,
        app_id: str,
    ) -> None:
        """Initialize remove button."""
        super().__init__(coordinator, app_id)
        self._attr_unique_id = f"{DOMAIN}_{app_id}_remove"
        self._attr_name = "Remove"
        self._attr_icon = "mdi:delete"
        self._attr_entity_category = EntityCategory.CONFIG

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Removing app %s", self.app_id)
        await self.coordinator.remove_app(self.app_id, remove_data=False)
