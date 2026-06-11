"""The Home Agent integration — autonomous IA for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import (
    async_track_time_change,
    async_track_time_interval,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .agent import HomeAgent
from .automation_manager import AutomationManager
from .chroma_client import ChromaClient, ChromaConnectionError
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
    DEFAULT_SECURITY_INTERVAL,
    DOMAIN,
)
from .gemini_client import GeminiClient, GeminiConnectionError
from .memory_manager import MemoryManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Agent from a config entry."""
    # Get configuration
    api_key = entry.data[CONF_GEMINI_API_KEY]
    model = entry.options.get(
        CONF_GEMINI_MODEL,
        entry.data.get(CONF_GEMINI_MODEL, DEFAULT_GEMINI_MODEL),
    )
    check_interval = entry.options.get(
        CONF_CHECK_INTERVAL,
        entry.data.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL),
    )
    chroma_url = entry.options.get(
        CONF_CHROMA_URL,
        entry.data.get(CONF_CHROMA_URL, DEFAULT_CHROMA_URL),
    )
    notify_service = entry.options.get(
        CONF_NOTIFY_SERVICE,
        entry.data.get(CONF_NOTIFY_SERVICE, DEFAULT_NOTIFY_SERVICE),
    )

    _LOGGER.info(
        "Setting up Home Agent (model=%s, interval=%dmin, chroma=%s)",
        model, check_interval, chroma_url,
    )

    # Create clients
    gemini = GeminiClient(hass, api_key, model)
    chroma = ChromaClient(hass, chroma_url)

    # Test connections
    try:
        await gemini.test_connection()
    except GeminiConnectionError as err:
        raise ConfigEntryNotReady(f"Cannot connect to Gemini: {err}") from err

    try:
        await chroma.heartbeat()
    except ChromaConnectionError as err:
        raise ConfigEntryNotReady(f"Cannot connect to ChromaDB: {err}") from err

    # Ensure ChromaDB collection exists
    await chroma.ensure_collection()

    # Create managers
    memory = MemoryManager(gemini, chroma)
    automation = AutomationManager(hass)
    agent = HomeAgent(hass, gemini, memory, automation, notify_service)

    # Create coordinator for periodic checks
    async def _async_update_data():
        try:
            return await agent.periodic_check()
        except Exception as err:
            raise UpdateFailed(f"Check failed: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=_async_update_data,
        update_interval=timedelta(minutes=check_interval),
    )

    # Initial data (don't run a check yet, just build state)
    coordinator.data = await agent.get_coordinator_data()

    # Store in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "agent": agent,
        "gemini": gemini,
        "chroma": chroma,
        "memory": memory,
        "unsub_listeners": [],
    }

    # Forward to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    from .services import async_setup_services
    await async_setup_services(hass)

    # Setup security check timer (every 5 minutes)
    async def _security_check_callback(_now):
        try:
            await agent.security_check()
            coordinator.async_set_updated_data(
                await agent.get_coordinator_data()
            )
        except Exception as err:
            _LOGGER.error("Security check failed: %s", err)

    unsub_security = async_track_time_interval(
        hass, _security_check_callback,
        timedelta(minutes=DEFAULT_SECURITY_INTERVAL),
    )

    # Setup daily automation review at 3:00 AM
    async def _automation_review_callback(_now):
        try:
            await agent.automation_review()
            coordinator.async_set_updated_data(
                await agent.get_coordinator_data()
            )
        except Exception as err:
            _LOGGER.error("Automation review failed: %s", err)

    unsub_review = async_track_time_change(
        hass, _automation_review_callback, hour=3, minute=0, second=0,
    )

    # Store unsub callbacks for cleanup
    hass.data[DOMAIN][entry.entry_id]["unsub_listeners"] = [
        unsub_security,
        unsub_review,
    ]

    # Register update listener for options
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Home Agent setup complete")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Home Agent")

    # Cancel timers
    entry_data = hass.data[DOMAIN].get(entry.entry_id, {})
    for unsub in entry_data.get("unsub_listeners", []):
        unsub()

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        if not hass.data[DOMAIN]:
            from .services import async_unload_services
            await async_unload_services(hass)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    _LOGGER.info("Reloading Home Agent due to config changes")
    await hass.config_entries.async_reload(entry.entry_id)
