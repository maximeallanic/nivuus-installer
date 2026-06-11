"""Home state collector for Home Agent."""
from __future__ import annotations

from datetime import datetime

from homeassistant.core import HomeAssistant

# Specific entities
PRESENCE_ENTITIES = ["person.maxime_allanic"]
ALARM_ENTITIES = ["alarm_control_panel.maison"]
CLIMATE_ENTITIES = ["climate.radiateur"]
SUN_ENTITIES = ["sun.sun"]
TV_ENTITIES = ["media_player.philips_google_tv_ta1"]

# Alarm semantic context — maps HA alarm states to AI-readable annotations
_ALARM_CONTEXT: dict[str, dict] = {
    "disarmed": {
        "interior_motion_expected": True,
        "description": "alarm off, residents expected to be home and active",
    },
    "armed_home": {
        "interior_motion_expected": True,
        "description": "armed in home mode, perimeter only, interior motion is normal",
    },
    "armed_night": {
        "interior_motion_expected": True,
        "description": (
            "armed in night mode, residents asleep, "
            "interior motion is normal (bathroom, water, pets)"
        ),
    },
    "armed_away": {
        "interior_motion_expected": False,
        "description": "armed in away mode, no one should be inside, any motion is suspicious",
    },
    "armed_vacation": {
        "interior_motion_expected": False,
        "description": "armed in vacation mode, extended absence, any activity is suspicious",
    },
    "triggered": {
        "interior_motion_expected": False,
        "description": "ALARM TRIGGERED — possible intrusion, immediate action required",
    },
    "arming": {
        "interior_motion_expected": True,
        "description": "alarm is arming (exit delay), motion expected during exit",
    },
    "pending": {
        "interior_motion_expected": True,
        "description": "alarm pending (entry delay), someone entering, awaiting disarm code",
    },
}

# Pattern filters
LIGHT_PATTERNS = ["lumiere", "bureau", "hotte"]
DOOR_PATTERNS = ["ouverture", "porte"]
MOTION_PATTERNS = ["mouvement", "occupation"]
TEMP_PATTERNS = ["temperature", "humidite"]
PRINTER_PATTERNS = ["p1s"]
SLEEP_MODE_PATTERNS = ["adaptive_lighting_sleep_mode"]


def gather_home_state(hass: HomeAssistant) -> str:
    """Collect current home state as structured Markdown text."""
    sections = []
    now = datetime.now()
    sections.append(
        f"## Contexte\nDate: {now.strftime('%A %d %B %Y %H:%M')}"
    )

    # Presence
    sections.append(_collect_specific(hass, "Présence", PRESENCE_ENTITIES))

    # Alarm (with semantic annotation)
    sections.append(_collect_alarm_annotated(hass))

    # Climate with details
    lines = ["## Chauffage"]
    for eid in CLIMATE_ENTITIES:
        state = hass.states.get(eid)
        if state:
            attrs = state.attributes
            lines.append(
                f"- {eid}: {state.state}, "
                f"preset={attrs.get('preset_mode', '?')}, "
                f"current={attrs.get('current_temperature', '?')}°C, "
                f"target={attrs.get('temperature', '?')}°C"
            )
    sections.append("\n".join(lines))

    # Lights
    sections.append(
        _collect_by_pattern(hass, "Lumières", "light", LIGHT_PATTERNS,
                           extra_attr="brightness")
    )

    # Doors/Windows
    sections.append(
        _collect_by_pattern(hass, "Portes & Fenêtres", "binary_sensor",
                           DOOR_PATTERNS)
    )

    # Motion
    sections.append(
        _collect_by_pattern(hass, "Mouvement", "binary_sensor",
                           MOTION_PATTERNS)
    )

    # Temperature & Humidity
    lines = ["## Climat intérieur"]
    for state in hass.states.async_all("sensor"):
        name = state.entity_id.lower()
        if any(p in name for p in TEMP_PATTERNS):
            unit = state.attributes.get("unit_of_measurement", "")
            lines.append(f"- {state.entity_id}: {state.state} {unit}")
    sections.append("\n".join(lines))

    # Low batteries
    lines = ["## Batteries faibles"]
    for state in hass.states.async_all("sensor"):
        if state.attributes.get("device_class") == "battery":
            try:
                if float(state.state) < 20:
                    lines.append(f"- {state.entity_id}: {state.state}%")
            except (ValueError, TypeError):
                pass
    sections.append("\n".join(lines))

    # Sun
    lines = ["## Soleil"]
    for eid in SUN_ENTITIES:
        state = hass.states.get(eid)
        if state:
            lines.append(
                f"- {eid}: {state.state} "
                f"(elevation={state.attributes.get('elevation', '?')}°)"
            )
    sections.append("\n".join(lines))

    # Weather
    lines = ["## Météo"]
    for state in hass.states.async_all("weather"):
        attrs = state.attributes
        lines.append(
            f"- {state.entity_id}: {state.state}, "
            f"temp={attrs.get('temperature', '?')}°C, "
            f"humidity={attrs.get('humidity', '?')}%"
        )
    sections.append("\n".join(lines))

    # TV
    sections.append(_collect_specific(hass, "TV", TV_ENTITIES))

    # Vacuums
    lines = ["## Aspirateurs"]
    for state in hass.states.async_all("vacuum"):
        lines.append(
            f"- {state.entity_id}: {state.state}, "
            f"battery={state.attributes.get('battery_level', '?')}%"
        )
    sections.append("\n".join(lines))

    # 3D Printer
    lines = ["## Imprimante 3D"]
    for state in hass.states.async_all("sensor"):
        name = state.entity_id.lower()
        if any(p in name for p in PRINTER_PATTERNS) and "etat" in name:
            lines.append(f"- {state.entity_id}: {state.state}")
    sections.append("\n".join(lines))

    # Sleep modes
    sections.append(
        _collect_by_pattern(hass, "Modes nuit", "switch",
                           SLEEP_MODE_PATTERNS)
    )

    # Ventilation
    lines = ["## Aération"]
    aere = hass.states.get("binary_sensor.maison_aere")
    if aere:
        lines.append(f"- binary_sensor.maison_aere: {aere.state}")
    sections.append("\n".join(lines))

    return "\n\n".join(sections)


def _collect_specific(
    hass: HomeAssistant, title: str, entity_ids: list[str]
) -> str:
    """Collect states for specific entity IDs."""
    lines = [f"## {title}"]
    for eid in entity_ids:
        state = hass.states.get(eid)
        if state:
            lines.append(f"- {eid}: {state.state}")
    return "\n".join(lines)


def gather_security_state(hass: HomeAssistant) -> str:
    """Collect security-relevant state only (presence, alarm, doors, motion, low batteries)."""
    sections = []
    now = datetime.now()
    sections.append(
        f"## Contexte\nDate: {now.strftime('%A %d %B %Y %H:%M')}"
    )

    # Presence
    sections.append(_collect_specific(hass, "Présence", PRESENCE_ENTITIES))

    # Alarm (with semantic annotation)
    sections.append(_collect_alarm_annotated(hass))

    # Doors/Windows
    sections.append(
        _collect_by_pattern(hass, "Portes & Fenêtres", "binary_sensor",
                           DOOR_PATTERNS)
    )

    # Motion
    sections.append(
        _collect_by_pattern(hass, "Mouvement", "binary_sensor",
                           MOTION_PATTERNS)
    )

    # Critical batteries (< 15%)
    lines = ["## Batteries critiques"]
    for state in hass.states.async_all("sensor"):
        if state.attributes.get("device_class") == "battery":
            try:
                if float(state.state) < 15:
                    lines.append(f"- {state.entity_id}: {state.state}%")
            except (ValueError, TypeError):
                pass
    sections.append("\n".join(lines))

    return "\n\n".join(sections)


def _collect_alarm_annotated(hass: HomeAssistant) -> str:
    """Collect alarm state with semantic annotation for the AI."""
    lines = ["## Alarme"]
    for eid in ALARM_ENTITIES:
        state = hass.states.get(eid)
        if not state:
            continue

        alarm_state = state.state
        ctx = _ALARM_CONTEXT.get(alarm_state, {})
        desc = ctx.get("description", alarm_state)
        motion_expected = ctx.get("interior_motion_expected", True)

        # Summarize presence
        presence_parts = []
        for pid in PRESENCE_ENTITIES:
            ps = hass.states.get(pid)
            if ps:
                name = ps.attributes.get("friendly_name", pid)
                presence_parts.append(f"{name} is {ps.state}")
        presence_summary = "; ".join(presence_parts) if presence_parts else "unknown"

        # Detect conflict: armed_away but someone is home
        conflict = ""
        if alarm_state in ("armed_away", "armed_vacation"):
            home_persons = [
                hass.states.get(p)
                for p in PRESENCE_ENTITIES
                if hass.states.get(p) and hass.states.get(p).state == "home"
            ]
            if home_persons:
                conflict = " WARNING: alarm is armed-away but persons are home"

        annotation = (
            f"[{desc}; {presence_summary}; "
            f"interior_motion_expected={'yes' if motion_expected else 'no'}"
            f"{conflict}]"
        )
        lines.append(f"- {eid}: {alarm_state} {annotation}")

    return "\n".join(lines)


def _collect_by_pattern(
    hass: HomeAssistant,
    title: str,
    domain: str,
    patterns: list[str],
    extra_attr: str | None = None,
) -> str:
    """Collect states for entities matching name patterns."""
    lines = [f"## {title}"]
    for state in hass.states.async_all(domain):
        name = state.entity_id.lower()
        if any(p in name for p in patterns):
            extra = ""
            if extra_attr:
                val = state.attributes.get(extra_attr, "")
                if val:
                    extra = f" ({extra_attr}={val})"
            lines.append(f"- {state.entity_id}: {state.state}{extra}")
    return "\n".join(lines)
