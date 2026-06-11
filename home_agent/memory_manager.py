"""RAG memory orchestration for Home Agent."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from .chroma_client import ChromaClient, ChromaConnectionError
from .gemini_client import GeminiClient, GeminiConnectionError

_LOGGER = logging.getLogger(__name__)

SEASONS = {
    12: "hiver", 1: "hiver", 2: "hiver",
    3: "printemps", 4: "printemps", 5: "printemps",
    6: "été", 7: "été", 8: "été",
    9: "automne", 10: "automne", 11: "automne",
}

DAYS_FR = {
    0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
    4: "Vendredi", 5: "Samedi", 6: "Dimanche",
}


class MemoryManager:
    """Orchestrates RAG memory: save, query, format."""

    def __init__(
        self,
        gemini: GeminiClient,
        chroma: ChromaClient,
    ) -> None:
        self.gemini = gemini
        self.chroma = chroma

    async def remember(
        self,
        state_summary: str,
        actions_taken: list[dict[str, Any]],
        result: str,
    ) -> None:
        """Save an experience to memory."""
        now = datetime.now()
        actions_str = ", ".join(
            f"{a.get('type')}: {a.get('entity_id', a.get('service', ''))}"
            for a in actions_taken
        ) if actions_taken else "aucune action"

        document = (
            f"{now.strftime('%Y-%m-%d %H:%M')} | {state_summary} | "
            f"Actions: {actions_str} | Résultat: {result}"
        )

        metadata = {
            "hour": now.hour,
            "day_of_week": now.weekday(),
            "day_name": DAYS_FR[now.weekday()],
            "season": SEASONS[now.month],
            "actions_count": len(actions_taken),
        }

        try:
            embedding = await self.gemini.embed(document)
            doc_id = now.strftime("%Y%m%d_%H%M%S_%f")
            await self.chroma.add(
                doc_id=doc_id,
                embedding=embedding,
                document=document,
                metadata=metadata,
            )
            _LOGGER.debug("Memory saved: %s", doc_id)
        except (GeminiConnectionError, ChromaConnectionError) as err:
            _LOGGER.warning("Failed to save memory: %s", err)

    async def recall(self, current_state: str, n: int = 5) -> str:
        """Recall similar past experiences for context."""
        try:
            embedding = await self.gemini.embed(current_state)
            results = await self.chroma.query(embedding, n_results=n)
        except (GeminiConnectionError, ChromaConnectionError) as err:
            _LOGGER.warning("Failed to recall memories: %s", err)
            return ""

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return ""

        lines = ["## Souvenirs similaires"]
        for i, (doc, meta, dist) in enumerate(
            zip(documents, metadatas, distances), 1
        ):
            day_name = meta.get("day_name", "?")
            hour = meta.get("hour", "?")
            similarity = round((1 - dist) * 100, 1)
            lines.append(
                f"{i}. [{day_name} {hour}h, similarité {similarity}%] {doc}"
            )

        return "\n".join(lines)

    async def get_memories_count(self) -> int:
        """Get total number of stored memories."""
        try:
            return await self.chroma.count()
        except ChromaConnectionError:
            return 0
