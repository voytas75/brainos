from __future__ import annotations

import os
from typing import Any

from .errors import EmbeddingProviderNotConfiguredError, EmbeddingRuntimeError, ValidationError
from .litellm_bootstrap import import_litellm_quietly
from .logging_utils import suppress_litellm_noise


DEFAULT_EMBEDDING_PROFILE = "brainos-embedding-default"
ENV_EMBEDDING_MODEL = "BRAINOS_EMBEDDING_MODEL"
ENV_AZURE_API_BASE = "AZURE_API_BASE"
ENV_AZURE_API_KEY = "AZURE_API_KEY"
ENV_AZURE_API_VERSION = "AZURE_API_VERSION"


class LiteLLMEmbeddingAdapter:
    def __init__(self, profile: str = DEFAULT_EMBEDDING_PROFILE):
        self.profile = profile

    def contract(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "provider_path": "litellm",
            "operational_provider": "azure",
            "required_env": [
                ENV_EMBEDDING_MODEL,
                ENV_AZURE_API_BASE,
                ENV_AZURE_API_KEY,
                ENV_AZURE_API_VERSION,
            ],
        }

    def _resolve_config(self) -> dict[str, str]:
        model = os.getenv(ENV_EMBEDDING_MODEL, "").strip()
        api_base = os.getenv(ENV_AZURE_API_BASE, "").strip()
        api_key = os.getenv(ENV_AZURE_API_KEY, "").strip()
        api_version = os.getenv(ENV_AZURE_API_VERSION, "").strip()

        missing = [
            name
            for name, value in [
                (ENV_EMBEDDING_MODEL, model),
                (ENV_AZURE_API_BASE, api_base),
                (ENV_AZURE_API_KEY, api_key),
                (ENV_AZURE_API_VERSION, api_version),
            ]
            if not value
        ]
        if missing:
            raise EmbeddingProviderNotConfiguredError(
                f"missing embedding environment variables: {', '.join(missing)}"
            )

        return {
            "model": model,
            "api_base": api_base,
            "api_key": api_key,
            "api_version": api_version,
        }

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
                    model=cfg["model"],
                    input=texts,
                    api_base=cfg["api_base"],
                    api_key=cfg["api_key"],
                    api_version=cfg["api_version"],
                )
        except Exception as exc:
            raise EmbeddingRuntimeError(f"embedding provider call failed: {exc}") from exc

        vectors = [item["embedding"] for item in response.data]
        dimensions = len(vectors[0]) if vectors else 0
        return {
            "vectors": vectors,
            "dimensions": dimensions,
            "provider": "azure",
            "model": cfg["model"],
            "profile": self.profile,
            "requested_count": len(texts),
            "returned_count": len(vectors),
        }
