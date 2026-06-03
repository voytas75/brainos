from __future__ import annotations

from typing import Any

from .embedding_config import (
    DEFAULT_EMBEDDING_PROFILE,
    ENV_AZURE_API_BASE,
    ENV_AZURE_API_KEY,
    ENV_AZURE_API_VERSION,
    ENV_EMBEDDING_MODEL,
    resolve_embedding_config,
)
from .errors import EmbeddingRuntimeError, ValidationError
from .litellm_bootstrap import import_litellm_quietly
from .logging_utils import suppress_litellm_noise


class LiteLLMEmbeddingAdapter:
    def __init__(self, profile: str = DEFAULT_EMBEDDING_PROFILE):
        self.profile = profile

    def contract(self) -> dict[str, Any]:
        try:
            return resolve_embedding_config(profile=self.profile)
        except Exception:
            return {
                "profile": self.profile,
                "provider_path": "litellm",
                "operational_provider": "unknown",
                "required_env": [ENV_EMBEDDING_MODEL],
            }

    def _resolve_config(self) -> dict[str, Any]:
        return resolve_embedding_config(profile=self.profile)

    def embed_texts(self, texts: list[str]) -> dict[str, Any]:
        if not isinstance(texts, list) or any(not isinstance(text, str) for text in texts):
            raise ValidationError("texts must be a list of strings")
        if not texts:
            raise ValidationError("texts must not be empty")

        cfg = self._resolve_config()
        litellm = import_litellm_quietly()

        try:
            with suppress_litellm_noise():
                response = litellm.embedding(
                    input=texts,
                    **cfg["call_params"],
                )
        except Exception as exc:
            raise EmbeddingRuntimeError(f"embedding provider call failed: {exc}") from exc

        vectors = [item["embedding"] for item in response.data]
        dimensions = len(vectors[0]) if vectors else 0
        return {
            "vectors": vectors,
            "dimensions": dimensions,
            "provider": cfg["operational_provider"],
            "model": cfg["model"],
            "profile": self.profile,
            "requested_count": len(texts),
            "returned_count": len(vectors),
        }
