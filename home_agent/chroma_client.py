"""ChromaDB REST API v2 client for Home Agent."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CHROMA_COLLECTION

_LOGGER = logging.getLogger(__name__)


class ChromaConnectionError(Exception):
    """Raised when connection to ChromaDB fails."""


class ChromaClient:
    """Client for ChromaDB v2 REST API."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str = "http://localhost:8000",
    ) -> None:
        self.hass = hass
        self.base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None
        self._collection_id: str | None = None
        self._tenant: str = "default_tenant"
        self._database: str = "default_database"

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = async_get_clientsession(self.hass)
        return self._session

    async def heartbeat(self) -> dict[str, Any]:
        """Check ChromaDB health."""
        url = f"{self.base_url}/api/v2/heartbeat"
        try:
            async with self.session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            raise ChromaConnectionError(
                f"Cannot connect to ChromaDB: {err}"
            ) from err

    async def ensure_collection(self) -> str:
        """Get or create the memories collection. Returns collection ID."""
        if self._collection_id:
            return self._collection_id

        base = f"{self.base_url}/api/v2"
        url = (
            f"{base}/tenants/{self._tenant}/databases/{self._database}"
            f"/collections"
        )

        # Try to get existing collection
        try:
            async with self.session.get(
                url,
                params={"name": CHROMA_COLLECTION},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    collections = await response.json()
                    if collections:
                        self._collection_id = collections[0]["id"]
                        return self._collection_id
        except aiohttp.ClientError:
            pass

        # Create collection
        try:
            async with self.session.post(
                url,
                json={
                    "name": CHROMA_COLLECTION,
                    "metadata": {"hnsw:space": "cosine"},
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self._collection_id = data["id"]
                _LOGGER.info("Created ChromaDB collection: %s", CHROMA_COLLECTION)
                return self._collection_id
        except aiohttp.ClientError as err:
            raise ChromaConnectionError(
                f"Failed to create collection: {err}"
            ) from err

    async def add(
        self,
        doc_id: str,
        embedding: list[float],
        document: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a document with embedding to the collection."""
        collection_id = await self.ensure_collection()
        base = f"{self.base_url}/api/v2"
        url = (
            f"{base}/tenants/{self._tenant}/databases/{self._database}"
            f"/collections/{collection_id}/add"
        )

        body: dict[str, Any] = {
            "ids": [doc_id],
            "embeddings": [embedding],
            "documents": [document],
        }
        if metadata:
            body["metadatas"] = [metadata]

        try:
            async with self.session.post(
                url,
                json=body,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to add to ChromaDB: %s", err)
            raise ChromaConnectionError(
                f"Failed to add document: {err}"
            ) from err

    async def query(
        self,
        embedding: list[float],
        n_results: int = 5,
    ) -> dict[str, Any]:
        """Query similar documents by embedding vector."""
        collection_id = await self.ensure_collection()
        base = f"{self.base_url}/api/v2"
        url = (
            f"{base}/tenants/{self._tenant}/databases/{self._database}"
            f"/collections/{collection_id}/query"
        )

        body = {
            "query_embeddings": [embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }

        try:
            async with self.session.post(
                url,
                json=body,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("ChromaDB query failed: %s", err)
            raise ChromaConnectionError(
                f"Query failed: {err}"
            ) from err

    async def count(self) -> int:
        """Get the number of documents in the collection."""
        collection_id = await self.ensure_collection()
        base = f"{self.base_url}/api/v2"
        url = (
            f"{base}/tenants/{self._tenant}/databases/{self._database}"
            f"/collections/{collection_id}/count"
        )

        try:
            async with self.session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError:
            return 0
