# BrainOS implementation notes

## What was implemented from the PDF

### Included now
- SQLite single-file storage core
- WAL mode
- foreign keys
- JSON validation for JSON-bearing columns
- working / episodic / semantic / procedural / ledger layers
- FTS5 full-text search for episodes
- chained ledger hashes with `previous_hash`
- indexes named in the PDF excerpt

### Deferred or made optional
- `sqlite-vec` is optional because the runtime extension may be unavailable
- full cognitive execution loop is not fully specifiable from the provided PDF excerpt
- session-based vector partitioning for >100k episodes is noted but not yet implemented

## Spec gaps noticed
- excerpt ends before the execution flow is fully defined
- the PDF DDL for `episodes_fts` and `episodes` does not specify a trigger strategy; this implementation mirrors rows in application code
- the PDF ledger schema did not include `previous_hash`, but the narrative requires cryptographic chaining; this field was added explicitly
- accepted edge predicates in code are not hard-enforced yet; the PDF presents them as vocabulary examples rather than a strict enum

## Suggested next slice
1. optional embedding provider abstraction
2. vector table integration with runtime capability detection
3. retrieval API combining FTS + vector + graph neighborhood
4. explicit cognitive loop orchestration
5. migration/versioning support
