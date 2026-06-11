"""Config flow for Home Agent integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_CHECK_INTERVAL,
    CONF_CHROMA_URL,
    CONF_GEMINI_API_KEY,
    CONF_GEMINI_MODEL,
    CONF_NOTIFY_SERVICE,
    DEFAULT_CHECK_INTERVAL,
    DEFAULT_CHROMA_URL,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_NOTIFY_SERVICE,
    DOMAIN,
    GEMINI_MODELS,
)

_LOGGER = logging.getLogger(__name__)


async def validate_gemini(hass: HomeAssistant, api_key: str, model: str) -> None:
    """Validate Gemini API connection."""
    from .gemini_client import GeminiClient, GeminiConnectionError

    client = GeminiClient(hass, api_key, model)
    try:
        await client.test_connection()
    except GeminiConnectionError as err:
        raise err


async def validate_chroma(hass: HomeAssistant, url: str) -> None:
    """Validate ChromaDB connection."""
    from .chroma_client import ChromaClient, ChromaConnectionError

    client = ChromaClient(hass, url)
    try:
        await client.heartbeat()
    except ChromaConnectionError as err:
        raise err


class HomeAgentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Home Agent."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}

        if user_input is not None:
            # Validate Gemini
            try:
                await validate_gemini(
                    self.hass,
                    user_input[CONF_GEMINI_API_KEY],
                    user_input.get(CONF_GEMINI_MODEL, DEFAULT_GEMINI_MODEL),
                )
            except Exception:
                errors["base"] = "cannot_connect_gemini"

            # Validate ChromaDB
            if not errors:
                try:
                    await validate_chroma(
                        self.hass,
                        user_input.get(CONF_CHROMA_URL, DEFAULT_CHROMA_URL),
                    )
                except Exception:
                    errors["base"] = "cannot_connect_chroma"

            if not errors:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Home Agent",
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_GEMINI_API_KEY): cv.string,
                vol.Optional(
                    CONF_GEMINI_MODEL, default=DEFAULT_GEMINI_MODEL
                ): vol.In(GEMINI_MODELS),
                vol.Optional(
                    CONF_CHECK_INTERVAL, default=DEFAULT_CHECK_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
                vol.Optional(
                    CONF_CHROMA_URL, default=DEFAULT_CHROMA_URL
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return HomeAgentOptionsFlowHandler(config_entry)


class HomeAgentOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Home Agent."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_model = self.config_entry.options.get(
            CONF_GEMINI_MODEL,
            self.config_entry.data.get(CONF_GEMINI_MODEL, DEFAULT_GEMINI_MODEL),
        )
        current_interval = self.config_entry.options.get(
            CONF_CHECK_INTERVAL,
            self.config_entry.data.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL),
        )
        current_chroma = self.config_entry.options.get(
            CONF_CHROMA_URL,
            self.config_entry.data.get(CONF_CHROMA_URL, DEFAULT_CHROMA_URL),
        )
        current_notify = self.config_entry.options.get(
            CONF_NOTIFY_SERVICE,
            self.config_entry.data.get(CONF_NOTIFY_SERVICE, DEFAULT_NOTIFY_SERVICE),
        )

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_GEMINI_MODEL, default=current_model
                ): vol.In(GEMINI_MODELS),
                vol.Optional(
                    CONF_CHECK_INTERVAL, default=current_interval
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
                vol.Optional(
                    CONF_CHROMA_URL, default=current_chroma
                ): cv.string,
                vol.Optional(
                    CONF_NOTIFY_SERVICE, default=current_notify
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )
