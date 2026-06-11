"""Config flow for Docker Marketplace integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CATALOG_PATH,
    CONF_DOCKER_HOST,
    CONF_STACKS_PATH,
    DEFAULT_CATALOG_PATH,
    DEFAULT_DOCKER_HOST,
    DEFAULT_STACKS_PATH,
    DOMAIN,
    NAME,
)
from .docker_client import DockerClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DOCKER_HOST, default=DEFAULT_DOCKER_HOST): str,
        vol.Required(CONF_CATALOG_PATH, default=DEFAULT_CATALOG_PATH): str,
        vol.Required(CONF_STACKS_PATH, default=DEFAULT_STACKS_PATH): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input."""
    docker_host = data[CONF_DOCKER_HOST]

    # Test Docker connection
    client = DockerClient(docker_host)
    if not await client.connect():
        raise CannotConnect(f"Cannot connect to Docker at {docker_host}")

    client.close()

    return {"title": NAME}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Docker Marketplace."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
