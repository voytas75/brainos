from brainos.benchmark import benchmark_cases


EXPECTED_REALISTIC_QUERY_CLASSES = {
    "sqlite wal durability",
    "what helps BrainOS keep local writes safe?",
    "azure embedding model",
    "what is the current BrainOS embedding path?",
    "how to repair stale vectors",
    "what should I do after runtime changes to vectors?",
    "disabled vector runtime",
    "what does disabled vector state usually point to?",
    "policy version explain",
    "what should retrieval explain show?",
}


def test_benchmark_cases_anchor_remains_small_and_realistic() -> None:
    fake_ids = {
        "ep_sqlite_wal": "ep1",
        "ep_embedding_azure": "ep2",
        "ep_reindex_runtime": "ep3",
        "ep_disabled_runtime": "ep4",
        "ep_policy_version": "ep5",
    }
    cases = benchmark_cases(fake_ids)

    queries = {item["query"] for item in cases}
    assert queries == EXPECTED_REALISTIC_QUERY_CLASSES
    assert len(cases) == 10


def test_benchmark_cases_anchor_stays_bounded_by_design() -> None:
    fake_ids = {
        "ep_sqlite_wal": "ep1",
        "ep_embedding_azure": "ep2",
        "ep_reindex_runtime": "ep3",
        "ep_disabled_runtime": "ep4",
        "ep_policy_version": "ep5",
    }
    cases = benchmark_cases(fake_ids)
    assert len(cases) <= 12

    unique_prefix_groups = {
        "storage": {"sqlite wal durability", "what helps BrainOS keep local writes safe?"},
        "embedding": {"azure embedding model", "what is the current BrainOS embedding path?"},
        "maintenance": {"how to repair stale vectors", "what should I do after runtime changes to vectors?"},
        "runtime": {"disabled vector runtime", "what does disabled vector state usually point to?"},
        "policy": {"policy version explain", "what should retrieval explain show?"},
    }
    queries = {item["query"] for item in cases}
    for expected_group in unique_prefix_groups.values():
        assert expected_group.issubset(queries)
