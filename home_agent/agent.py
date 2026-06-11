"""Core Home Agent — autonomous IA for Home Assistant."""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.core import HomeAssistant

from .automation_manager import AutomationManager
from .const import (
    AUTOMATION_REVIEW_PROMPT,
    KILL_SWITCH_ENTITY,
    MAIN_PROMPT,
    NOTIFICATION_DEDUP_COOLDOWN,
    NOTIFICATION_RATE_LIMIT,
    RESPONSE_SCHEMA,
    SECURITY_NOTIFICATION_RATE_LIMIT,
    SECURITY_PROMPT,
    STATE_ANALYZING,
    STATE_ERROR,
    STATE_EXECUTING,
    STATE_IDLE,
)
from .gemini_client import GeminiClient, GeminiConnectionError
from .memory_manager import MemoryManager
from .state_collector import gather_home_state, gather_security_state

_LOGGER = logging.getLogger(__name__)


class HomeAgent:
    """Autonomous Home Agent that manages the house."""

    def __init__(
        self,
        hass: HomeAssistant,
        gemini: GeminiClient,
        memory: MemoryManager,
        automation: AutomationManager,
        notify_service: str = "mobile_app_pixel_10_pro",
    ) -> None:
        self.hass = hass
        self.gemini = gemini
        self.memory = memory
        self.automation = automation
        self.notify_service = notify_service
        self._actions_today: int = 0
        self._last_reset_day: int = datetime.now().day
        self._status: str = STATE_IDLE
        self._last_error: str | None = None
        self._last_analysis: str = ""
        self._last_actions: list[dict[str, Any]] = []
        self._last_alerts: list[str] = []
        self._last_decision_time: datetime | None = None
        self._start_time: datetime = datetime.now(timezone.utc)
        self._notification_timestamps: list[datetime] = []
        self._security_notification_timestamps: list[datetime] = []
        self._recent_notification_hashes: dict[str, datetime] = {}

    def _reset_daily_counter(self) -> None:
        """Reset actions counter at midnight."""
        today = datetime.now().day
        if today != self._last_reset_day:
            self._actions_today = 0
            self._last_reset_day = today

    async def get_coordinator_data(self) -> dict[str, Any]:
        """Build data dict for the coordinator/sensors."""
        memories_count = await self.memory.get_memories_count()
        return {
            "status": self._status,
            "last_error": self._last_error,
            "uptime": str(datetime.now(timezone.utc) - self._start_time),
            "memories_count": memories_count,
            "last_decision_time": self._last_decision_time,
            "analysis": self._last_analysis,
            "actions_count": len(self._last_actions),
            "actions_detail": self._last_actions,
            "alerts": self._last_alerts,
            "actions_today": self._actions_today,
        }

    async def periodic_check(self) -> dict[str, Any]:
        """Main periodic check cycle (15 min)."""
        return await self._run_check(MAIN_PROMPT, "periodic")

    async def security_check(self) -> dict[str, Any]:
        """Security-focused check (5 min)."""
        return await self._run_check(SECURITY_PROMPT, "security")

    async def automation_review(self) -> dict[str, Any]:
        """Daily automation review (3h AM)."""
        return await self._run_check(AUTOMATION_REVIEW_PROMPT, "automation_review")

    async def _run_check(
        self, system_prompt: str, check_type: str
    ) -> dict[str, Any]:
        """Execute a check cycle."""
        self._reset_daily_counter()

        # Check kill switch
        kill_state = self.hass.states.get(KILL_SWITCH_ENTITY)
        if kill_state and kill_state.state != "on":
            _LOGGER.debug("Kill switch is off, skipping %s check", check_type)
            return await self.get_coordinator_data()

        self._status = STATE_ANALYZING
        _LOGGER.info("Starting %s check", check_type)

        try:
            # Gather home state (filtered for security checks)
            if check_type == "security":
                state_text = gather_security_state(self.hass)
            else:
                state_text = gather_home_state(self.hass)

            # Recall similar memories
            memories_text = await self.memory.recall(state_text)

            # Build full prompt
            user_prompt = self._build_user_prompt(
                state_text, memories_text, check_type
            )

            # Call Gemini
            response = await self.gemini.generate(
                system_prompt, user_prompt, RESPONSE_SCHEMA
            )

            # Parse response
            analysis = response.get("analysis", "")
            actions = response.get("actions", [])
            alerts = response.get("alerts", [])

            self._last_analysis = analysis
            self._last_alerts = alerts
            self._last_decision_time = datetime.now(timezone.utc)

            _LOGGER.info(
                "[%s] Analysis: %s | Actions: %d | Alerts: %d",
                check_type, analysis[:100], len(actions), len(alerts),
            )

            # Execute actions
            if actions:
                self._status = STATE_EXECUTING
                executed = await self._execute_actions(actions, check_type)
                self._last_actions = executed
            else:
                self._last_actions = []

            # Fire event
            self.hass.bus.async_fire(
                "home_agent_check_complete",
                {
                    "type": check_type,
                    "analysis": analysis,
                    "actions_count": len(actions),
                    "alerts": alerts,
                },
            )

            # Save memory only when something happened
            if self._last_actions or alerts:
                state_summary = state_text[:500]
                result = f"OK - {len(self._last_actions)} actions executed"
                await self.memory.remember(
                    state_summary, self._last_actions, result
                )

            self._status = STATE_IDLE
            self._last_error = None

        except GeminiConnectionError as err:
            self._status = STATE_ERROR
            self._last_error = str(err)
            _LOGGER.error("Gemini error during %s: %s", check_type, err)

        except Exception as err:
            self._status = STATE_ERROR
            self._last_error = str(err)
            _LOGGER.exception("Unexpected error during %s: %s", check_type, err)

        return await self.get_coordinator_data()

    def _build_user_prompt(
        self, state_text: str, memories_text: str, check_type: str
    ) -> str:
        """Build the user prompt with state + memories."""
        parts = [
            f"## État actuel de la maison ({check_type})\n",
            state_text,
        ]

        if memories_text:
            parts.append(f"\n{memories_text}")

        # Add automation list for review checks
        if check_type == "automation_review":
            parts.append("\n## Automatisations existantes")
            states = self.hass.states.async_all("automation")
            for s in states:
                attrs = s.attributes
                parts.append(
                    f"- {s.entity_id}: state={s.state}, "
                    f"last_triggered={attrs.get('last_triggered', 'never')}, "
                    f"name={attrs.get('friendly_name', '')}"
                )

        return "\n".join(parts)

    def _can_send_notification(self) -> bool:
        """Check rate limit: max N notifications per hour (periodic)."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=1)
        self._notification_timestamps = [
            ts for ts in self._notification_timestamps if ts > cutoff
        ]
        return len(self._notification_timestamps) < NOTIFICATION_RATE_LIMIT

    def _can_send_security_notification(self) -> bool:
        """Check rate limit: max N notifications per hour (security)."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=1)
        self._security_notification_timestamps = [
            ts for ts in self._security_notification_timestamps if ts > cutoff
        ]
        return (
            len(self._security_notification_timestamps)
            < SECURITY_NOTIFICATION_RATE_LIMIT
        )

    def _is_duplicate_notification(self, action: dict[str, Any]) -> bool:
        """Check if the same notification was already sent recently."""
        data = action.get("data", {})
        title = data.get("title", "Home Agent")
        message = data.get("message") or action.get("reason", "")
        raw = f"{title}|{message}"
        h = hashlib.sha256(raw.encode()).hexdigest()[:16]

        now = datetime.now(timezone.utc)
        cooldown = timedelta(minutes=NOTIFICATION_DEDUP_COOLDOWN)

        # Purge expired entries
        self._recent_notification_hashes = {
            k: v
            for k, v in self._recent_notification_hashes.items()
            if now - v < cooldown
        }

        if h in self._recent_notification_hashes:
            return True

        self._recent_notification_hashes[h] = now
        return False

    async def _execute_actions(
        self, actions: list[dict[str, Any]], check_type: str = "periodic"
    ) -> list[dict[str, Any]]:
        """Execute the actions returned by Gemini."""
        executed = []

        for action in actions:
            action_type = action.get("type", "")
            reason = action.get("reason", "")

            try:
                if action_type == "service_call":
                    await self._execute_service_call(action)
                    executed.append(action)
                    self._actions_today += 1

                elif action_type == "create_automation":
                    config = action.get("data", {})
                    if config:
                        success = await self.automation.create_automation(config)
                        if success:
                            executed.append(action)
                            self._actions_today += 1

                elif action_type == "disable_automation":
                    entity_id = action.get("entity_id", "")
                    if entity_id:
                        success = await self.automation.disable_automation(
                            entity_id
                        )
                        if success:
                            executed.append(action)
                            self._actions_today += 1

                elif action_type == "notification":
                    is_security = check_type == "security"
                    allowed = (
                        self._can_send_security_notification()
                        if is_security
                        else self._can_send_notification()
                    )
                    if allowed:
                        if self._is_duplicate_notification(action):
                            _LOGGER.warning(
                                "Duplicate notification suppressed: %s",
                                reason,
                            )
                        else:
                            await self._send_notification(action)
                            now_ts = datetime.now(timezone.utc)
                            if is_security:
                                self._security_notification_timestamps.append(
                                    now_ts
                                )
                            self._notification_timestamps.append(now_ts)
                            executed.append(action)
                            self._actions_today += 1
                    else:
                        limit = (
                            SECURITY_NOTIFICATION_RATE_LIMIT
                            if is_security
                            else NOTIFICATION_RATE_LIMIT
                        )
                        _LOGGER.warning(
                            "Notification rate limited (%d/h), skipping: %s",
                            limit,
                            reason,
                        )

                else:
                    _LOGGER.warning("Unknown action type: %s", action_type)

                _LOGGER.info(
                    "Action executed: %s — %s", action_type, reason
                )

            except Exception as err:
                _LOGGER.error(
                    "Failed to execute action %s: %s", action_type, err
                )

        return executed

    async def _execute_service_call(self, action: dict[str, Any]) -> None:
        """Execute a service call action."""
        service = action.get("service", "")
        entity_id = action.get("entity_id", "")
        data = action.get("data", {})

        if "." not in service:
            _LOGGER.error("Invalid service format: %s", service)
            return

        domain, service_name = service.split(".", 1)

        service_data = dict(data) if data else {}
        if entity_id:
            service_data["entity_id"] = entity_id

        await self.hass.services.async_call(
            domain, service_name, service_data, blocking=True
        )

    async def _send_notification(self, action: dict[str, Any]) -> None:
        """Send a notification."""
        data = action.get("data", {})
        message = (
            data.get("message")
            or action.get("reason")
            or "Notification Home Agent"
        )
        title = data.get("title", "Home Agent")

        await self.hass.services.async_call(
            "notify",
            self.notify_service,
            {"message": message, "title": title},
            blocking=True,
        )
