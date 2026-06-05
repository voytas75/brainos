# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added typed episode ingest normalization via `src/brainos/ingest.py` to standardize episode content and metadata before persistence.
- Added CLI support for typed episode fields on `episode-add`, including `--kind`, `--topic`, and `--source`.
- Added vector runtime preflight in `src/brainos/retrieval_runtime.py` to distinguish runtime misconfiguration from ordinary retrieval misses.
- Added retrieval smoke coverage via `scripts/retrieval_smoke.sh` and supporting documentation in `docs/retrieval-green-path-smoke-test.md`.
- Added tests for ingest normalization, retrieval runtime posture, explain evidence clarity, explain signal alignment, typed ingest operational flow, and decision reachability.
- Added project notes documenting the bounded retrieval/ingest hardening series and related real-usage observations.

### Changed
- Changed episode persistence in `src/brainos/store.py` so new episodes are normalized on write.
- Changed retrieval ranking in `src/brainos/retrieval.py` to improve reachability of `decision`, `procedure`, and other typed episodes for action-oriented queries.
- Changed `src/brainos/explain.py` to expose clearer operator-facing retrieval diagnostics, including runtime status, operator summary, confidence hint, top-hit evidence, comparison hint, and zero-hit reasoning.
- Changed retrieval diagnostics so mixed vector-led hits with lexical support are classified explicitly and aligned with operator summaries.
- Changed migration test expectations to validate compatibility with the current schema version instead of pinning to version 3.
- Changed README and API docs to document the retrieval green-path smoke flow and updated explain diagnostics behavior.

### Fixed
- Fixed the ambiguity between "no good hit" and "vector runtime is misconfigured" by surfacing explicit runtime posture in retrieval outputs.
- Fixed CLI/test expectations to match the current explain diagnostic behavior for degraded-but-still-lexically-usable retrieval paths.
