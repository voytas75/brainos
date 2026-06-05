#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${1:-/tmp/brainos-retrieval-smoke-$(date +%Y%m%d-%H%M%S).db}"
OUT_DIR="${2:-./artifacts/retrieval-smoke}"
SESSION_ID="retrieval-smoke"

mkdir -p "$OUT_DIR"
rm -f "$DB_PATH"

uv run brainos --db "$DB_PATH" init >/dev/null

uv run brainos --db "$DB_PATH" episode-add "$SESSION_ID" 'W Polsce wdrożenie AI Act obejmuje projekt ustawy tworzącej organ nadzoru i piaskownice regulacyjne.' --metadata-json '{"source":"retrieval_smoke","topic":"regulation"}' >/dev/null
uv run brainos --db "$DB_PATH" episode-add "$SESSION_ID" 'Polskie firmy mają wysoki poziom zainteresowania AI, ale wdrożenia blokują koszty, kompetencje i dostęp do mocy obliczeniowej.' --metadata-json '{"source":"retrieval_smoke","topic":"adoption"}' >/dev/null
uv run brainos --db "$DB_PATH" episode-add "$SESSION_ID" 'Państwo deklaruje rozwój krajowej infrastruktury AI i wsparcie dla polskich modeli językowych.' --metadata-json '{"source":"retrieval_smoke","topic":"infrastructure"}' >/dev/null

uv run brainos --db "$DB_PATH" vector-index-sync-batch --object-type episode --vector-status missing > "$OUT_DIR/vector-sync.json"
uv run brainos --db "$DB_PATH" recall 'AI Act w Polsce nadzor i piaskownice' --session-id "$SESSION_ID" > "$OUT_DIR/recall.json"
uv run brainos --db "$DB_PATH" retrieval-explain 'AI Act w Polsce nadzor i piaskownice' --session-id "$SESSION_ID" > "$OUT_DIR/explain.json"
uv run brainos --db "$DB_PATH" retrieval-health > "$OUT_DIR/health.json"

python3 - <<'PY' "$DB_PATH" "$OUT_DIR"
import json
import sys
from pathlib import Path

db_path = sys.argv[1]
out_dir = Path(sys.argv[2])
recall = json.loads((out_dir / 'recall.json').read_text())
explain = json.loads((out_dir / 'explain.json').read_text())
health = json.loads((out_dir / 'health.json').read_text())

runtime = recall.get('retrieval_runtime') or {}
top_ranked = explain.get('top_ranked_episodes') or []
status = 'PASS'
notes = []

if runtime.get('status') != 'ok':
    status = 'FAIL'
    notes.append(f"runtime_not_ready:{runtime.get('status')}")
if not top_ranked:
    status = 'FAIL'
    notes.append('no_ranked_hits')
if health.get('status') != 'ok':
    status = 'WEAK' if status == 'PASS' else status
    notes.append(f"health_status:{health.get('status')}")

top1 = top_ranked[0] if top_ranked else {}
summary = {
    'ok': status == 'PASS',
    'status': status,
    'db_path': db_path,
    'purpose': 'retrieval green-path smoke test',
    'not_a_quality_benchmark': True,
    'checks': {
        'runtime_status': runtime.get('status'),
        'top_ranked_count': len(top_ranked),
        'health_status': health.get('status'),
        'top1_preview': top1.get('content'),
    },
    'notes': notes,
    'artifacts': {
        'vector_sync': str(out_dir / 'vector-sync.json'),
        'recall': str(out_dir / 'recall.json'),
        'explain': str(out_dir / 'explain.json'),
        'health': str(out_dir / 'health.json'),
    },
}
(out_dir / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
