"""Service handlers for Home Agent integration."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    DOMAIN,
    SERVICE_RUN_AUTOMATION_REVIEW,
    SERVICE_RUN_CHECK,
    SERVICE_RUN_SECURITY_CHECK,
)

_LOGGER = logging.getLogger(__name__)


def _get_agent(hass: HomeAssistant):
    """Get HomeAgent instance from hass.data."""
    if DOMAIN not in hass.data or not hass.data[DOMAIN]:
        raise ValueError("Home Agent integration not set up")
    entry_id = list(hass.data[DOMAIN].keys())[0]
    return hass.data[DOMAIN][entry_id]["agent"]


async def async_handle_run_check(call: ServiceCall) -> None:
    """Handle run_check service call."""
    _LOGGER.info("Manual check triggered")
    agent = _get_agent(call.hass)
    coordinator = list(call.hass.data[DOMAIN].values())[0]["coordinator"]
    await agent.periodic_check()
    coordinator.async_set_updated_data(await agent.get_coordinator_data())


async def async_handle_run_security_check(call: ServiceCall) -> None:
    """Handle run_security_check service call."""
    _LOGGER.info("Manual security check triggered")
    agent = _get_agent(call.hass)
    coordinator = list(call.hass.data[DOMAIN].values())[0]["coordinator"]
    await agent.security_check()
    coordinator.async_set_updated_data(await agent.get_coordinator_data())


async def async_handle_run_automation_review(call: ServiceCall) -> None:
    """Handle run_automation_review service call."""
    _LOGGER.info("Manual automation review triggered")
    agent = _get_agent(call.hass)
    coordinator = list(call.hass.data[DOMAIN].values())[0]["coordinator"]
    await agent.automation_review()
    coordinator.async_set_updated_data(await agent.get_coordinator_data())


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register Home Agent services."""
    hass.services.async_register(
        DOMAIN, SERVICE_RUN_CHECK, async_handle_run_check
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RUN_SECURITY_CHECK, async_handle_run_security_check
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RUN_AUTOMATION_REVIEW, async_handle_run_automation_review
    )
    _LOGGER.info("Home Agent services registered")


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unregister Home Agent services."""
    hass.services.async_remove(DOMAIN, SERVICE_RUN_CHECK)
    hass.services.async_remove(DOMAIN, SERVICE_RUN_SECURITY_CHECK)
    hass.services.async_remove(DOMAIN, SERVICE_RUN_AUTOMATION_REVIEW)
    _LOGGER.info("Home Agent services unregistered")
