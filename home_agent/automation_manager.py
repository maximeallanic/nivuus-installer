"""Automation CRUD manager for Home Agent."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

_PROTECTED_KEYWORDS = (
    "alarm", "alerte", "security", "securite", "sécurité",
    "intrusion", "lock", "verrou", "smoke", "fire",
    "flood", "fuite", "incendie", "urgence", "emergency",
)


class AutomationManager:
    """Manage HA automations via hass services and REST API."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def list_automations(self) -> list[dict[str, Any]]:
        """List all automations with their state and last_triggered."""
        automations = []
        states = self.hass.states.async_all("automation")

        for state in states:
            attrs = state.attributes
            automations.append({
                "entity_id": state.entity_id,
                "state": state.state,
                "friendly_name": attrs.get("friendly_name", ""),
                "last_triggered": str(attrs.get("last_triggered", "")),
                "id": attrs.get("id", ""),
            })

        return automations

    async def create_automation(self, config: dict[str, Any]) -> bool:
        """Create a new automation via HA REST API."""
        try:
            from homeassistant.helpers.aiohttp_client import (
                async_get_clientsession,
            )
            import aiohttp

            session = async_get_clientsession(self.hass)
            ha_url = "http://localhost:8123"

            # Get long-lived token from supervisor or use internal API
            headers = {
                "Authorization": f"Bearer {self._get_token()}",
                "Content-Type": "application/json",
            }

            async with session.post(
                f"{ha_url}/api/config/automation/config",
                json=config,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status in (200, 201):
                    _LOGGER.info("Automation created: %s", config.get("alias"))
                    return True
                text = await response.text()
                _LOGGER.error("Failed to create automation: %s", text)
                return False

        except Exception as err:
            _LOGGER.error("Error creating automation: %s", err)
            return False

    async def update_automation(
        self, automation_id: str, config: dict[str, Any]
    ) -> bool:
        """Update an existing automation config."""
        try:
            from homeassistant.helpers.aiohttp_client import (
                async_get_clientsession,
            )
            import aiohttp

            session = async_get_clientsession(self.hass)
            ha_url = "http://localhost:8123"
            headers = {
                "Authorization": f"Bearer {self._get_token()}",
                "Content-Type": "application/json",
            }

            async with session.put(
                f"{ha_url}/api/config/automation/config/{automation_id}",
                json=config,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Automation updated: %s", automation_id)
                    return True
                text = await response.text()
                _LOGGER.error("Failed to update automation: %s", text)
                return False

        except Exception as err:
            _LOGGER.error("Error updating automation: %s", err)
            return False

    async def disable_automation(self, entity_id: str) -> bool:
        """Disable an automation via service call (blocked for protected ones)."""
        # Check entity_id against protected keywords
        eid_lower = entity_id.lower()
        if any(kw in eid_lower for kw in _PROTECTED_KEYWORDS):
            _LOGGER.warning(
                "BLOCKED: cannot disable protected automation %s", entity_id
            )
            return False

        # Check friendly_name against protected keywords
        state = self.hass.states.get(entity_id)
        if state:
            fname = state.attributes.get("friendly_name", "").lower()
            if any(kw in fname for kw in _PROTECTED_KEYWORDS):
                _LOGGER.warning(
                    "BLOCKED: cannot disable protected automation %s (%s)",
                    entity_id,
                    fname,
                )
                return False

        try:
            await self.hass.services.async_call(
                "automation",
                "turn_off",
                {"entity_id": entity_id},
                blocking=True,
            )
            _LOGGER.info("Automation disabled: %s", entity_id)
            return True
        except Exception as err:
            _LOGGER.error("Error disabling automation %s: %s", entity_id, err)
            return False

    async def enable_automation(self, entity_id: str) -> bool:
        """Enable an automation via service call."""
        try:
            await self.hass.services.async_call(
                "automation",
                "turn_on",
                {"entity_id": entity_id},
                blocking=True,
            )
            _LOGGER.info("Automation enabled: %s", entity_id)
            return True
        except Exception as err:
            _LOGGER.error("Error enabling automation %s: %s", entity_id, err)
            return False

    def _get_token(self) -> str:
        """Get authentication token for local API calls."""
        # Use the Supervisor token if available (Docker HA)
        import os
        token = os.environ.get("SUPERVISOR_TOKEN", "")
        if not token:
            token = os.environ.get("HASSIO_TOKEN", "")
        return token
