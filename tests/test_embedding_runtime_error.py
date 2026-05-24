import pytest

from brainos.embedding import LiteLLMEmbeddingAdapter
from brainos.errors import EmbeddingRuntimeError


class _BoomLiteLLM:
    @staticmethod
    def embedding(**kwargs):
        raise RuntimeError("401 bad key")


def test_embedding_adapter_maps_provider_failure_to_brainos_error(monkeypatch):
    monkeypatch.setenv("BRAINOS_EMBEDDING_MODEL", "azure/test-embed")
    monkeypatch.setenv("AZURE_API_BASE", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_API_VERSION", "2024-10-21")
    monkeypatch.setitem(__import__("sys").modules, "litellm", _BoomLiteLLM)

    adapter = LiteLLMEmbeddingAdapter()
    with pytest.raises(EmbeddingRuntimeError) as exc:
        adapter.embed_texts(["hello"])
    assert "embedding provider call failed" in str(exc.value)
