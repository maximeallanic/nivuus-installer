"""Gemini API client for Home Agent."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
EMBEDDING_MODEL = "gemini-embedding-001"
MAX_RETRIES = 3
RETRY_BACKOFF = [5, 10, 20]


class GeminiConnectionError(Exception):
    """Raised when connection to Gemini API fails."""


class GeminiClient:
    """Client for Google Gemini REST API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
        model: str = "gemini-2.0-flash",
    ) -> None:
        self.hass = hass
        self.api_key = api_key
        self.model = model
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = async_get_clientsession(self.hass)
        return self._session

    async def test_connection(self) -> dict[str, Any]:
        """Test Gemini API connectivity by fetching model info."""
        url = f"{GEMINI_API_BASE}/models/{self.model}?key={self.api_key}"
        try:
            async with self.session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 401 or response.status == 403:
                    raise GeminiConnectionError("Invalid API key")
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            raise GeminiConnectionError(
                f"Cannot connect to Gemini API (model={self.model})"
            ) from err

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict[str, Any] | None = None,
        _retry_count: int = 0,
    ) -> dict[str, Any]:
        """Generate content using Gemini with structured JSON output."""
        url = (
            f"{GEMINI_API_BASE}/models/{self.model}:generateContent"
            f"?key={self.api_key}"
        )

        body: dict[str, Any] = {
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3,
            },
        }

        if response_schema:
            body["generationConfig"]["responseSchema"] = response_schema

        try:
            _LOGGER.debug(
                "Gemini generate: model=%s, prompt_len=%d",
                self.model, len(user_prompt),
            )
            async with self.session.post(
                url,
                json=body,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as response:
                if response.status in (429, 503):
                    return await self._retry_or_raise(
                        response.status, system_prompt, user_prompt,
                        response_schema, _retry_count,
                    )
                response.raise_for_status()
                data = await response.json()

            # Extract the text from the response
            candidates = data.get("candidates", [])
            if not candidates:
                raise GeminiConnectionError("No candidates in Gemini response")

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise GeminiConnectionError("No parts in Gemini response")

            text = parts[0].get("text", "")
            return json.loads(text)

        except json.JSONDecodeError as err:
            _LOGGER.error("Failed to parse Gemini JSON response: %s", err)
            raise GeminiConnectionError(
                f"Invalid JSON from Gemini: {err}"
            ) from err
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            # Timeout and connection errors are retryable
            return await self._retry_or_raise(
                "timeout" if isinstance(err, asyncio.TimeoutError) else "error",
                system_prompt, user_prompt, response_schema, _retry_count,
            )
        except asyncio.CancelledError:
            raise GeminiConnectionError("Gemini request was cancelled")
        except GeminiConnectionError:
            raise
        except Exception as err:
            raise GeminiConnectionError(
                f"Unexpected Gemini error (model={self.model})"
            ) from err

    async def _retry_or_raise(
        self,
        reason: int | str,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict[str, Any] | None,
        retry_count: int,
    ) -> dict[str, Any]:
        """Retry the request or raise if max retries exceeded."""
        if retry_count >= MAX_RETRIES:
            raise GeminiConnectionError(
                f"Gemini {reason} after {MAX_RETRIES} retries "
                f"(model={self.model})"
            )
        delay = RETRY_BACKOFF[retry_count]
        _LOGGER.warning(
            "Gemini %s, retry %d/%d in %ds",
            reason, retry_count + 1, MAX_RETRIES, delay,
        )
        await asyncio.sleep(delay)
        return await self.generate(
            system_prompt, user_prompt, response_schema,
            _retry_count=retry_count + 1,
        )

    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector for text using gemini-embedding-001."""
        url = (
            f"{GEMINI_API_BASE}/models/{EMBEDDING_MODEL}:embedContent"
            f"?key={self.api_key}"
        )

        body = {
            "content": {"parts": [{"text": text}]},
        }

        try:
            async with self.session.post(
                url,
                json=body,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                response.raise_for_status()
                data = await response.json()

            embedding = data.get("embedding", {})
            values = embedding.get("values", [])
            if not values:
                raise GeminiConnectionError("No embedding values in response")
            return values

        except aiohttp.ClientError as err:
            raise GeminiConnectionError(
                "Embedding request failed"
            ) from err
