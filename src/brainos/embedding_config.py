from __future__ import annotations

import os
from typing import Any

from .errors import EmbeddingProviderNotConfiguredError


DEFAULT_EMBEDDING_PROFILE = "brainos-embedding-default"
ENV_EMBEDDING_MODEL = "BRAINOS_EMBEDDING_MODEL"
ENV_EMBEDDING_PROVIDER = "BRAINOS_EMBEDDING_PROVIDER"
ENV_EMBEDDING_API_BASE = "BRAINOS_EMBEDDING_API_BASE"
ENV_EMBEDDING_API_KEY = "BRAINOS_EMBEDDING_API_KEY"
ENV_EMBEDDING_API_VERSION = "BRAINOS_EMBEDDING_API_VERSION"
ENV_EMBEDDING_HEADERS_JSON = "BRAINOS_EMBEDDING_HEADERS_JSON"
ENV_AZURE_API_BASE = "AZURE_API_BASE"
ENV_AZURE_API_KEY = "AZURE_API_KEY"
ENV_AZURE_API_VERSION = "AZURE_API_VERSION"
ENV_OPENAI_API_KEY = "OPENAI_API_KEY"


def _getenv(name: str) -> str:
    return os.getenv(name, "").strip()


def _infer_provider(model: str, explicit: str) -> str:
    if explicit:
        return explicit
    if "/" in model:
        prefix = model.split("/", 1)[0].strip().lower()
        if prefix:
            return prefix
    return "unknown"


def _provider_required_env(provider: str, api_base: str, api_key: str, api_version: str) -> list[str]:
    required = [ENV_EMBEDDING_MODEL]
    if provider == "azure":
        required.extend([ENV_AZURE_API_BASE, ENV_AZURE_API_KEY, ENV_AZURE_API_VERSION])
    elif provider == "openai":
        required.append(ENV_OPENAI_API_KEY)
        if api_base:
            required.append(ENV_EMBEDDING_API_BASE)
        if api_version:
            required.append(ENV_EMBEDDING_API_VERSION)
    else:
        if api_base:
            required.append(ENV_EMBEDDING_API_BASE)
        if api_key:
            required.append(ENV_EMBEDDING_API_KEY)
        if api_version:
            required.append(ENV_EMBEDDING_API_VERSION)
    return required


def resolve_embedding_config(profile: str = DEFAULT_EMBEDDING_PROFILE) -> dict[str, Any]:
    model = _getenv(ENV_EMBEDDING_MODEL)
    explicit_provider = _getenv(ENV_EMBEDDING_PROVIDER).lower()

    if not model:
        raise EmbeddingProviderNotConfiguredError(
            f"missing embedding environment variables: {ENV_EMBEDDING_MODEL}"
        )

    provider = _infer_provider(model, explicit_provider)

    api_base = _getenv(ENV_EMBEDDING_API_BASE)
    api_key = _getenv(ENV_EMBEDDING_API_KEY)
    api_version = _getenv(ENV_EMBEDDING_API_VERSION)

    config_source: dict[str, str] = {ENV_EMBEDDING_MODEL: ENV_EMBEDDING_MODEL}

    if provider == "azure":
        if not api_base:
            api_base = _getenv(ENV_AZURE_API_BASE)
            if api_base:
                config_source["api_base"] = ENV_AZURE_API_BASE
        else:
            config_source["api_base"] = ENV_EMBEDDING_API_BASE
        if not api_key:
            api_key = _getenv(ENV_AZURE_API_KEY)
            if api_key:
                config_source["api_key"] = ENV_AZURE_API_KEY
        else:
            config_source["api_key"] = ENV_EMBEDDING_API_KEY
        if not api_version:
            api_version = _getenv(ENV_AZURE_API_VERSION)
            if api_version:
                config_source["api_version"] = ENV_AZURE_API_VERSION
        else:
            config_source["api_version"] = ENV_EMBEDDING_API_VERSION
    elif provider == "openai":
        if not api_key:
            api_key = _getenv(ENV_OPENAI_API_KEY)
            if api_key:
                config_source["api_key"] = ENV_OPENAI_API_KEY
        else:
            config_source["api_key"] = ENV_EMBEDDING_API_KEY
        if api_base:
            config_source["api_base"] = ENV_EMBEDDING_API_BASE
        if api_version:
            config_source["api_version"] = ENV_EMBEDDING_API_VERSION
    else:
        if api_base:
            config_source["api_base"] = ENV_EMBEDDING_API_BASE
        if api_key:
            config_source["api_key"] = ENV_EMBEDDING_API_KEY
        if api_version:
            config_source["api_version"] = ENV_EMBEDDING_API_VERSION

    required_env = _provider_required_env(provider, api_base, api_key, api_version)
    present_env: list[str] = []
    missing_env: list[str] = []

    env_values = {
        ENV_EMBEDDING_MODEL: model,
        ENV_AZURE_API_BASE: api_base if provider == "azure" else _getenv(ENV_AZURE_API_BASE),
        ENV_AZURE_API_KEY: api_key if provider == "azure" else _getenv(ENV_AZURE_API_KEY),
        ENV_AZURE_API_VERSION: api_version if provider == "azure" else _getenv(ENV_AZURE_API_VERSION),
        ENV_OPENAI_API_KEY: api_key if provider == "openai" else _getenv(ENV_OPENAI_API_KEY),
        ENV_EMBEDDING_API_BASE: api_base,
        ENV_EMBEDDING_API_KEY: api_key,
        ENV_EMBEDDING_API_VERSION: api_version,
    }
    for name in required_env:
        if env_values.get(name, ""):
            present_env.append(name)
        else:
            missing_env.append(name)

    if missing_env:
        raise EmbeddingProviderNotConfiguredError(
            f"missing embedding environment variables: {', '.join(missing_env)}"
        )

    call_params: dict[str, Any] = {"model": model}
    if api_base:
        call_params["api_base"] = api_base
    if api_key:
        call_params["api_key"] = api_key
    if api_version:
        call_params["api_version"] = api_version

    return {
        "profile": profile,
        "provider_path": "litellm",
        "operational_provider": provider,
        "model": model,
        "required_env": required_env,
        "present_env": present_env,
        "missing_env": [],
        "call_params": call_params,
        "config_source": config_source,
        "headers_env": ENV_EMBEDDING_HEADERS_JSON,
    }
