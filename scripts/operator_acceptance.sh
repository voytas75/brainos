#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${1:-/tmp/brainos-operator-acceptance-$(date +%Y%m%d-%H%M%S).db}"
OUT_DIR="${2:-./artifacts/operator-acceptance}"
SESSION_ID="operator-acceptance"

mkdir -p "$OUT_DIR"
rm -f "$DB_PATH"

uv run brainos --db "$DB_PATH" init >/dev/null

uv run brainos --db "$DB_PATH" retrieval-health --benchmark-limit 5 > "$OUT_DIR/health-empty.json"

uv run brainos --db "$DB_PATH" episode-add "$SESSION_ID" 'BrainOS retrieval should stay operator-readable even when vector runtime is unavailable.' --metadata-json '{"source":"operator_acceptance","kind":"observation"}' >/dev/null
uv run brainos --db "$DB_PATH" episode-add "$SESSION_ID" 'Low-evidence databases should not be presented as ordinary ranking regressions.' --metadata-json '{"source":"operator_acceptance","kind":"fact"}' >/dev/null

uv run brainos --db "$DB_PATH" retrieval-health --benchmark-limit 5 > "$OUT_DIR/health-populated.json"
uv run brainos --db "$DB_PATH" retrieval-explain 'vector runtime unavailable' --session-id "$SESSION_ID" > "$OUT_DIR/explain-misconfigured.json"
uv run brainos --db "$DB_PATH" recall 'operator-readable retrieval' --session-id "$SESSION_ID" > "$OUT_DIR/recall-misconfigured.json"

python3 - <<'PY' "$DB_PATH" "$OUT_DIR"
import json
import sys
from pathlib import Path

db_path = sys.argv[1]
out_dir = Path(sys.argv[2])

def load(name: str):
    return json.loads((out_dir / name).read_text())

health_empty = load('health-empty.json')
health_populated = load('health-populated.json')
explain = load('explain-misconfigured.json')
recall = load('recall-misconfigured.json')

scenarios = []

scenarios.append({
    'name': 'runtime_issue_is_classified_before_quality_interpretation',
    'ok': health_populated.get('action_hint') == 'runtime_fix' and str(health_populated.get('summary', '')).startswith('runtime fix needed before vector-quality interpretation'),
    'observed': {
        'summary': health_populated.get('summary'),
        'action_hint': health_populated.get('action_hint'),
    },
})

scenarios.append({
    'name': 'empty_database_reports_low_evidence_before_population',
    'ok': health_empty.get('quality', {}).get('status') == 'low_evidence' and 'low_evidence_database' in (health_empty.get('quality', {}).get('notes') or []),
    'observed': {
        'quality_status': health_empty.get('quality', {}).get('status'),
        'quality_notes': health_empty.get('quality', {}).get('notes'),
    },
})

scenarios.append({
    'name': 'populated_runtime_issue_is_not_misreported_as_low_evidence',
    'ok': health_populated.get('quality', {}).get('status') != 'low_evidence',
    'observed': {
        'quality_status': health_populated.get('quality', {}).get('status'),
        'quality_notes': health_populated.get('quality', {}).get('notes'),
    },
})

scenarios.append({
    'name': 'misconfigured_runtime_still_reports_lexical_fallback_in_explain',
    'ok': explain.get('retrieval_runtime', {}).get('status') == 'misconfigured' and 'lexical retrieval may still work' in str(explain.get('operator_summary', '')),
    'observed': {
        'runtime_status': explain.get('retrieval_runtime', {}).get('status'),
        'operator_summary': explain.get('operator_summary'),
    },
})

scenarios.append({
    'name': 'misconfigured_runtime_keeps_direct_fix_hint',
    'ok': recall.get('retrieval_runtime', {}).get('action_hint') == 'configure_sqlite_vec_path',
    'observed': {
        'runtime_action_hint': recall.get('retrieval_runtime', {}).get('action_hint'),
        'runtime_status': recall.get('retrieval_runtime', {}).get('status'),
    },
})

scenarios.append({
    'name': 'explain_does_not_collapse_runtime_debug_into_generic_quality_debug',
    'ok': explain.get('diagnostic_hint') in {'inspect_vector_participation', 'lexical_grounded_top_hit', 'configure_sqlite_vec_path_before_quality_debug'},
    'observed': {
        'diagnostic_hint': explain.get('diagnostic_hint'),
    },
})

failed = [s['name'] for s in scenarios if not s['ok']]
summary = {
    'ok': not failed,
    'status': 'PASS' if not failed else 'FAIL',
    'db_path': db_path,
    'purpose': 'operator acceptance pack for runtime/degraded interpretation',
    'not_a_quality_benchmark': True,
    'scenario_count': len(scenarios),
    'failed_scenarios': failed,
    'scenarios': scenarios,
    'artifacts': {
        'health_empty': str(out_dir / 'health-empty.json'),
        'health_populated': str(out_dir / 'health-populated.json'),
        'explain': str(out_dir / 'explain-misconfigured.json'),
        'recall': str(out_dir / 'recall-misconfigured.json'),
    },
}
(out_dir / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
