from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalScoringPolicy:
    version: str
    vector_distance_cutoff: float
    dual_source_bonus: float
    lexical_vector_overlap_bonus: float
    low_overlap_vector_only_penalty: float
    semantic_name_match_bonus: float
    episode_vector_base: float
    semantic_vector_base: float


RETRIEVAL_SCORING_POLICY_V1 = RetrievalScoringPolicy(
    version="retrieval-scoring-v1",
    vector_distance_cutoff=1.2,
    dual_source_bonus=150.0,
    lexical_vector_overlap_bonus=80.0,
    low_overlap_vector_only_penalty=120.0,
    semantic_name_match_bonus=40.0,
    episode_vector_base=460.0,
    semantic_vector_base=420.0,
)
