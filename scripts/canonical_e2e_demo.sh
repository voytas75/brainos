#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${1:-./brain_canonical_e2e.db}"
OUT_DIR="${2:-./artifacts/canonical-e2e}"
ENABLE_VECTOR_SYNC="${BRAINOS_CANONICAL_E2E_ENABLE_VECTOR_SYNC:-0}"
SESSION_ID="canonical-e2e"

if [ -n "${BRAINOS_CLI:-}" ]; then
  # Allow callers to override the exact CLI command used by the demo.
  read -r -a BRAINOS_CMD <<< "$BRAINOS_CLI"
elif [ -x "./.venv/bin/brainos" ]; then
  BRAINOS_CMD=("./.venv/bin/brainos")
elif command -v brainos >/dev/null 2>&1; then
  BRAINOS_CMD=("brainos")
else
  BRAINOS_CMD=("uv" "run" "brainos")
fi

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"
rm -f "$DB_PATH"

("${BRAINOS_CMD[@]}" --db "$DB_PATH" init) >/dev/null
("${BRAINOS_CMD[@]}" --db "$DB_PATH" wm-set demo_state '{"mode":"canonical-e2e","status":"ready"}') > "$OUT_DIR/wm-set.txt"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" wm-get demo_state) > "$OUT_DIR/wm-get.json"

EP_SEM=$("${BRAINOS_CMD[@]}" --db "$DB_PATH" episode-add "$SESSION_ID" 'SQLite WAL keeps concurrent reads practical for the local BrainOS storage core.' --metadata-json '{"source":"canonical_demo","promotion_type":"semantic","semantic_name":"SQLite WAL concurrency","semantic_type":"Fact","semantic_properties":{"area":"storage","priority":"high"}}')
EP_PROC=$("${BRAINOS_CMD[@]}" --db "$DB_PATH" episode-add "$SESSION_ID" 'Canonical demo procedure: init db, run recall, inspect explain, verify ledger.' --metadata-json '{"source":"canonical_demo","promotion_type":"procedure","procedure_name":"canonical_demo_flow","procedure_steps":[{"step":"init-db"},{"step":"run-recall"},{"step":"inspect-explain"},{"step":"verify-ledger"}],"description":"Minimal BrainOS evaluation flow"}')
("${BRAINOS_CMD[@]}" --db "$DB_PATH" episode-add "$SESSION_ID" 'The canonical retrieval demo checks recall, retrieval explain, and retrieval health before broader claims are made.' --metadata-json '{"source":"canonical_demo","topic":"retrieval"}') >/dev/null
("${BRAINOS_CMD[@]}" --db "$DB_PATH" episode-add "$SESSION_ID" 'Decision support in BrainOS is operator-facing and bounded, not autonomous execution.' --metadata-json '{"source":"canonical_demo","topic":"decision"}') >/dev/null

("${BRAINOS_CMD[@]}" --db "$DB_PATH" schema-status) > "$OUT_DIR/schema-status.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" capabilities) > "$OUT_DIR/capabilities.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" embedding-readiness) > "$OUT_DIR/embedding-readiness.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" sqlite-vec-readiness) > "$OUT_DIR/sqlite-vec-readiness.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" vector-index-list --limit 20) > "$OUT_DIR/vector-index-list-before.json"

if [ "$ENABLE_VECTOR_SYNC" = "1" ]; then
  ("${BRAINOS_CMD[@]}" --db "$DB_PATH" vector-index-sync-batch --object-type episode --vector-status missing) > "$OUT_DIR/vector-sync.json"
else
  python3 - <<'PY' "$OUT_DIR/vector-sync.json"
import json
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(json.dumps({
    "ok": True,
    "mode": "skipped",
    "reason": "vector sync disabled by default for canonical demo",
    "action_hint": "set BRAINOS_CANONICAL_E2E_ENABLE_VECTOR_SYNC=1 if vector-ready evidence is desired",
}, ensure_ascii=False, indent=2))
PY
fi

("${BRAINOS_CMD[@]}" --db "$DB_PATH" recall 'canonical retrieval demo health' --session-id "$SESSION_ID" --limit 5) > "$OUT_DIR/recall.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" retrieval-explain 'canonical retrieval demo health' --session-id "$SESSION_ID" --limit 5) > "$OUT_DIR/explain.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" retrieval-health --benchmark-limit 5) > "$OUT_DIR/health.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" doctor --benchmark-limit 5) > "$OUT_DIR/doctor.json"

("${BRAINOS_CMD[@]}" --db "$DB_PATH" consolidation-preview "$EP_SEM") > "$OUT_DIR/preview-semantic.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" promote-episode "$EP_SEM") > "$OUT_DIR/promote-semantic.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" semantic-node-get "sem_${EP_SEM%%-*}") > "$OUT_DIR/semantic-node.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" consolidation-preview "$EP_PROC") > "$OUT_DIR/preview-procedure.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" promote-episode "$EP_PROC") > "$OUT_DIR/promote-procedure.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" procedure-list --limit 10) > "$OUT_DIR/procedure-list.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" ledger-verify) > "$OUT_DIR/ledger-verify.json"
("${BRAINOS_CMD[@]}" --db "$DB_PATH" vector-index-list --limit 20) > "$OUT_DIR/vector-index-list-after.json"

python3 - <<'PY' "$DB_PATH" "$OUT_DIR" "$ENABLE_VECTOR_SYNC"
import json
import sys
from pathlib import Path

db_path = sys.argv[1]
out_dir = Path(sys.argv[2])
enable_vector_sync = sys.argv[3] == "1"
parse_warnings = []

def load(name: str):
    text = (out_dir / name).read_text()
    decoder = json.JSONDecoder()
    obj, end = decoder.raw_decode(text)
    trailing = text[end:].strip()
    if trailing:
        parse_warnings.append(f"{name}:ignored_trailing_output")
    return obj

def is_ok(payload):
    if isinstance(payload, dict):
        if "status" in payload:
            return payload.get("status") == "ok"
        if "ok" in payload:
            return bool(payload.get("ok"))
    return True

schema = load("schema-status.json")
capabilities = load("capabilities.json")
embedding = load("embedding-readiness.json")
sqlite_vec = load("sqlite-vec-readiness.json")
vector_sync = load("vector-sync.json")
recall = load("recall.json")
explain = load("explain.json")
health = load("health.json")
doctor = load("doctor.json")
promote_semantic = load("promote-semantic.json")
promote_procedure = load("promote-procedure.json")
ledger_verify = load("ledger-verify.json")

core_failures = []
if not schema.get("is_current"):
    core_failures.append("schema_not_current")
if not ledger_verify.get("ok"):
    core_failures.append("ledger_verify_failed")
if not promote_semantic.get("ok"):
    core_failures.append("semantic_promotion_failed")
if not promote_procedure.get("ok"):
    core_failures.append("procedure_promotion_failed")
ranked_episodes = recall.get("ranked_episodes") or []
if not ranked_episodes:
    core_failures.append("no_ranked_recall_hits")

degraded_reasons = []
if vector_sync.get("mode") == "skipped":
    degraded_reasons.append("vector_sync_skipped_by_default")
if not is_ok(doctor):
    degraded_reasons.append(f"doctor_status:{doctor.get('status')}")
if not is_ok(health):
    degraded_reasons.append(f"health_status:{health.get('status')}")
if not is_ok(embedding):
    degraded_reasons.append(f"embedding_readiness:{embedding.get('status')}")
if not is_ok(sqlite_vec):
    degraded_reasons.append(f"sqlite_vec_readiness:{sqlite_vec.get('status', sqlite_vec.get('ok'))}")

if core_failures:
    overall_status = "FAIL"
elif degraded_reasons:
    overall_status = "DEGRADED"
else:
    overall_status = "PASS"

top_ranked = explain.get("top_ranked_episodes") or []
summary = {
    "ok": overall_status == "PASS",
    "overall_status": overall_status,
    "db_path": db_path,
    "purpose": "canonical bounded BrainOS e2e demo",
    "vector_sync_requested": enable_vector_sync,
    "not_a_broad_quality_claim": True,
    "checks": {
        "schema_current": schema.get("is_current"),
        "ledger_ok": ledger_verify.get("ok"),
        "semantic_promoted": promote_semantic.get("ok"),
        "procedure_promoted": promote_procedure.get("ok"),
        "ranked_recall_count": len(ranked_episodes),
        "top_recall_preview": ranked_episodes[0].get("content") if ranked_episodes else None,
        "top_explain_preview": top_ranked[0].get("content") if top_ranked else None,
        "doctor_status": doctor.get("status"),
        "health_status": health.get("status"),
        "benchmark_mode": ((health.get("quality") or {}).get("benchmark") or {}).get("mode"),
        "sqlite_vec_capability": capabilities.get("sqlite_vec"),
    },
    "core_failures": core_failures,
    "degraded_reasons": degraded_reasons,
    "artifact_parse_warnings": parse_warnings,
    "artifacts": {name: str(out_dir / name) for name in [
        "wm-get.json",
        "schema-status.json",
        "capabilities.json",
        "embedding-readiness.json",
        "sqlite-vec-readiness.json",
        "vector-sync.json",
        "recall.json",
        "explain.json",
        "health.json",
        "doctor.json",
        "preview-semantic.json",
        "promote-semantic.json",
        "semantic-node.json",
        "preview-procedure.json",
        "promote-procedure.json",
        "procedure-list.json",
        "ledger-verify.json",
        "vector-index-list-before.json",
        "vector-index-list-after.json",
    ]},
}
(out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
