"""Sensor platform for Home Agent integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ICON_AGENT,
    ICON_COUNTER,
    ICON_DECISION,
    SENSOR_ACTIONS_TODAY,
    SENSOR_LAST_DECISION,
    SENSOR_STATUS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Home Agent sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        HomeAgentStatusSensor(coordinator),
        HomeAgentLastDecisionSensor(coordinator),
        HomeAgentActionsTodaySensor(coordinator),
    ]

    async_add_entities(entities)


class HomeAgentStatusSensor(CoordinatorEntity, SensorEntity):
    """Home Agent status sensor (idle/analyzing/executing/error)."""

    _attr_name = "Home Agent Status"
    _attr_icon = ICON_AGENT

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{SENSOR_STATUS}"

    @property
    def native_value(self) -> str:
        if self.coordinator.data:
            return self.coordinator.data.get("status", "idle")
        return "idle"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if not self.coordinator.data:
            return {}
        return {
            "last_error": self.coordinator.data.get("last_error"),
            "uptime": self.coordinator.data.get("uptime"),
            "memories_count": self.coordinator.data.get("memories_count", 0),
        }


class HomeAgentLastDecisionSensor(CoordinatorEntity, SensorEntity):
    """Home Agent last decision sensor with analysis details."""

    _attr_name = "Home Agent Last Decision"
    _attr_icon = ICON_DECISION
    _attr_device_class = "timestamp"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{SENSOR_LAST_DECISION}"

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get("last_decision_time")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if not self.coordinator.data:
            return {}
        return {
            "analysis": self.coordinator.data.get("analysis", ""),
            "actions_count": self.coordinator.data.get("actions_count", 0),
            "actions_detail": self.coordinator.data.get("actions_detail", []),
            "alerts": self.coordinator.data.get("alerts", []),
        }


class HomeAgentActionsTodaySensor(CoordinatorEntity, SensorEntity):
    """Home Agent actions counter for today."""

    _attr_name = "Home Agent Actions Today"
    _attr_icon = ICON_COUNTER
    _attr_native_unit_of_measurement = "actions"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{SENSOR_ACTIONS_TODAY}"

    @property
    def native_value(self) -> int:
        if self.coordinator.data:
            return self.coordinator.data.get("actions_today", 0)
        return 0
