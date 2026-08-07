from __future__ import annotations

from typing import Any, cast

from .embedding_config import (
    DEFAULT_EMBEDDING_PROFILE,
    ENV_EMBEDDING_MODEL,
    resolve_embedding_config,
)
from .errors import (
    EmbeddingProviderNotConfiguredError,
    EmbeddingRuntimeError,
    ValidationError,
)
from .litellm_bootstrap import import_litellm_quietly
from .logging_utils import suppress_litellm_noise


def diagnostic_embedding_contract(config: dict[str, Any]) -> dict[str, Any]:
    raw_config_source = cast(dict[object, object], config.get("config_source") or {})
    config_source = {
        key: value
        for key, value in raw_config_source.items()
        if isinstance(key, str) and isinstance(value, str)
    }
    model = config.get("model")
    return {
        "profile": config.get("profile"),
        "provider_path": config.get("provider_path"),
        "operational_provider": config.get("operational_provider"),
        "model": model,
        "required_env": config.get("required_env") or [],
        "present_env": config.get("present_env") or [],
        "missing_env": config.get("missing_env") or [],
        "config_source": config_source,
        "headers_env": config.get("headers_env"),
        "api_key_present": "api_key" in config_source,
        "call_params": {"model": model} if model else {},
    }


class LiteLLMEmbeddingAdapter:
    def __init__(self, profile: str = DEFAULT_EMBEDDING_PROFILE):
        self.profile = profile

    def contract(self) -> dict[str, Any]:
        try:
            return diagnostic_embedding_contract(self._resolve_config())
        except EmbeddingProviderNotConfiguredError:
            return {
                "profile": self.profile,
                "provider_path": "litellm",
                "operational_provider": "unknown",
                "required_env": [ENV_EMBEDDING_MODEL],
            }

    def _resolve_config(self) -> dict[str, Any]:
        return resolve_embedding_config(profile=self.profile)

    def embed_texts(self, texts: Any) -> dict[str, Any]:
        if not isinstance(texts, list):
            raise ValidationError("texts must be a list of strings")
        raw_texts = cast(list[object], texts)
        if any(not isinstance(text, str) for text in raw_texts):
            raise ValidationError("texts must be a list of strings")
        if not raw_texts:
            raise ValidationError("texts must not be empty")

        typed_texts = cast(list[str], raw_texts)
        cfg = self._resolve_config()
        litellm = import_litellm_quietly()

        try:
            with suppress_litellm_noise():
                response = litellm.embedding(
                    input=typed_texts,
                    **cfg["call_params"],
                )
        except Exception as exc:
            raise EmbeddingRuntimeError(
                f"embedding provider call failed: {exc}"
            ) from exc

        vectors = cast(list[list[float]], [item["embedding"] for item in response.data])
        dimensions = len(vectors[0]) if vectors else 0
        return {
            "vectors": vectors,
            "dimensions": dimensions,
            "provider": cfg["operational_provider"],
            "model": cfg["model"],
            "profile": self.profile,
            "requested_count": len(typed_texts),
            "returned_count": len(vectors),
        }
