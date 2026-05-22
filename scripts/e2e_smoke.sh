#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${1:-./brain_e2e.db}"
SUMMARY_PATH="${2:-./artifacts/e2e-summary.json}"
mkdir -p "$(dirname "$SUMMARY_PATH")"
rm -f "$DB_PATH"

uv run brainos --db "$DB_PATH" init >/dev/null

EP1=$(uv run brainos --db "$DB_PATH" episode-add session-alpha 'SQLite WAL should stay enabled for concurrent reads' --metadata-json '{"kind":"fact","promotion_type":"semantic","semantic_name":"SQLite WAL concurrency","semantic_type":"Fact","semantic_properties":{"area":"storage","priority":"high"}}')
EP2=$(uv run brainos --db "$DB_PATH" episode-add session-alpha 'Bootstrap flow: init db, load state, verify ledger' --metadata-json '{"kind":"procedure","promotion_type":"procedure","procedure_name":"bootstrap_sequence","procedure_steps":[{"step":"init-db"},{"step":"load-state"},{"step":"verify-ledger"}],"description":"Initial BrainOS startup flow"}')
uv run brainos --db "$DB_PATH" episode-add session-beta 'BrainOS uses semantic nodes and edges for durable knowledge' --metadata-json '{"kind":"note"}' >/dev/null

uv run brainos --db "$DB_PATH" recall BrainOS --limit 10 > ./artifacts/recall.json
uv run brainos --db "$DB_PATH" consolidation-preview "$EP1" > ./artifacts/preview-semantic.json
uv run brainos --db "$DB_PATH" promote-episode "$EP1" > ./artifacts/promote-semantic.json
uv run brainos --db "$DB_PATH" semantic-node-get "sem_${EP1%%-*}" > ./artifacts/semantic-node.json
uv run brainos --db "$DB_PATH" consolidation-preview "$EP2" > ./artifacts/preview-procedure.json
uv run brainos --db "$DB_PATH" promote-episode "$EP2" > ./artifacts/promote-procedure.json
uv run brainos --db "$DB_PATH" procedure-list --limit 10 > ./artifacts/procedure-list.json
uv run brainos --db "$DB_PATH" ledger-verify > ./artifacts/ledger-verify.json
uv run brainos --db "$DB_PATH" schema-status > ./artifacts/schema-status.json
uv run brainos --db "$DB_PATH" capabilities > ./artifacts/capabilities.json

python3 - <<'PY' "$SUMMARY_PATH"
import json
import sys
from pathlib import Path
summary_path = Path(sys.argv[1])
art = Path('artifacts')
summary = {
    'ok': True,
    'artifacts': {
        'recall': json.loads((art / 'recall.json').read_text()),
        'preview_semantic': json.loads((art / 'preview-semantic.json').read_text()),
        'promote_semantic': json.loads((art / 'promote-semantic.json').read_text()),
        'semantic_node': json.loads((art / 'semantic-node.json').read_text()),
        'preview_procedure': json.loads((art / 'preview-procedure.json').read_text()),
        'promote_procedure': json.loads((art / 'promote-procedure.json').read_text()),
        'procedure_list': json.loads((art / 'procedure-list.json').read_text()),
        'ledger_verify': json.loads((art / 'ledger-verify.json').read_text()),
        'schema_status': json.loads((art / 'schema-status.json').read_text()),
        'capabilities': json.loads((art / 'capabilities.json').read_text()),
    }
}
summary['checks'] = {
    'ledger_ok': summary['artifacts']['ledger_verify']['ok'],
    'schema_current': summary['artifacts']['schema_status']['is_current'],
    'semantic_promoted': summary['artifacts']['promote_semantic']['ok'],
    'procedure_promoted': summary['artifacts']['promote_procedure']['ok'],
}
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps({'ok': True, 'summary_path': str(summary_path)}, ensure_ascii=False, indent=2))
PY
