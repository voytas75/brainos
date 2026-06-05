from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .env import load_project_env
from .errors import BrainOSError, SqliteVecReadinessError
from .benchmark import run_retrieval_benchmark
from .doctor import doctor_summary, embedding_readiness_summary
from .explain import explain_recall
from .health import retrieval_health_summary
from .real_corpus_probe import run_real_corpus_probe
from .store import BrainOSStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brainos")
    parser.add_argument("--db", default="brain.db", help="Path to SQLite database")

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize schema")
    p_init.add_argument("--enable-vector", action="store_true")

    p_wm_set = sub.add_parser("wm-set", help="Set working memory JSON value")
    p_wm_set.add_argument("key")
    p_wm_set.add_argument("value_json")

    p_wm_get = sub.add_parser("wm-get", help="Get working memory value")
    p_wm_get.add_argument("key")

    p_ep_add = sub.add_parser("episode-add", help="Add episodic memory entry")
    p_ep_add.add_argument("session_id")
    p_ep_add.add_argument("content")
    p_ep_add.add_argument("--metadata-json", default="{}")
    p_ep_add.add_argument("--kind")
    p_ep_add.add_argument("--topic")
    p_ep_add.add_argument("--source")

    p_ep_list = sub.add_parser("episodes-list", help="List episodes")
    p_ep_list.add_argument("--session-id")
    p_ep_list.add_argument("--limit", type=int, default=20)

    p_ep_preview = sub.add_parser("consolidation-preview", help="Preview promotion candidate for one episode")
    p_ep_preview.add_argument("episode_id")

    p_ep_promotion_get = sub.add_parser("episode-promotion-get", help="Get promotion state for one episode")
    p_ep_promotion_get.add_argument("episode_id")

    p_ep_promote = sub.add_parser("promote-episode", help="Promote one episode into semantic or procedural layer")
    p_ep_promote.add_argument("episode_id")

    p_ep_search = sub.add_parser("episode-search", help="Search episodes with FTS5")
    p_ep_search.add_argument("query")
    p_ep_search.add_argument("--session-id")
    p_ep_search.add_argument("--limit", type=int, default=10)

    p_recall = sub.add_parser("recall", help="Recall from episodic memory")
    p_recall.add_argument("query")
    p_recall.add_argument("--session-id")
    p_recall.add_argument("--limit", type=int, default=10)

    p_sem_node_upsert = sub.add_parser("semantic-node-upsert", help="Create or update semantic node")
    p_sem_node_upsert.add_argument("node_id")
    p_sem_node_upsert.add_argument("name")
    p_sem_node_upsert.add_argument("node_type")
    p_sem_node_upsert.add_argument("--properties-json", default="{}")

    p_sem_node_get = sub.add_parser("semantic-node-get", help="Get semantic node")
    p_sem_node_get.add_argument("node_id")

    p_sem_edge_upsert = sub.add_parser("semantic-edge-upsert", help="Create or update semantic edge")
    p_sem_edge_upsert.add_argument("source_id")
    p_sem_edge_upsert.add_argument("target_id")
    p_sem_edge_upsert.add_argument("predicate")
    p_sem_edge_upsert.add_argument("--weight", type=float, default=1.0)

    p_sem_edges_list = sub.add_parser("semantic-edges-list", help="List semantic edges for a node")
    p_sem_edges_list.add_argument("node_id")
    p_sem_edges_list.add_argument("--direction", choices=["out", "in", "both"], default="both")

    p_proc_create = sub.add_parser("procedure-create", help="Create procedure")
    p_proc_create.add_argument("name")
    p_proc_create.add_argument("steps_json")
    p_proc_create.add_argument("--description")

    p_proc_list = sub.add_parser("procedure-list", help="List procedures")
    p_proc_list.add_argument("--all", action="store_true")
    p_proc_list.add_argument("--limit", type=int, default=50)

    p_proc_get = sub.add_parser("procedure-get", help="Get procedure")
    p_proc_get.add_argument("procedure_id")

    p_decision_log = sub.add_parser("decision-log", help="Create or update decision-support object")
    p_decision_log.add_argument("question")
    p_decision_log.add_argument("--decision-id")
    p_decision_log.add_argument("--status", default="draft")
    p_decision_log.add_argument("--recommended-option-id")
    p_decision_log.add_argument("--operator-call-required", default="true")
    p_decision_log.add_argument("--options-json", required=True)
    p_decision_log.add_argument("--arguments-json", default="[]")
    p_decision_log.add_argument("--counterarguments-json", default="[]")
    p_decision_log.add_argument("--risks-json", default="[]")
    p_decision_log.add_argument("--missing-information-json", default="[]")
    p_decision_log.add_argument("--uncertainty-notes-json", default="[]")
    p_decision_log.add_argument("--metadata-json", default="{}")
    p_decision_log.add_argument("--review-after")

    p_decision_list = sub.add_parser("decision-list", help="List decision-support objects")
    p_decision_list.add_argument("--status")
    p_decision_list.add_argument("--limit", type=int, default=50)

    p_decision_get = sub.add_parser("decision-get", help="Get decision-support object")
    p_decision_get.add_argument("decision_id")

    p_inspect = sub.add_parser("inspect", help="Inspect one stored object with related provenance")
    p_inspect.add_argument("object_type", choices=["decision", "episode"])
    p_inspect.add_argument("object_id")

    p_decision_check = sub.add_parser("decision-check", help="Check one decision for caution/conflict signals")
    p_decision_check.add_argument("decision_id")

    p_decision_history = sub.add_parser("decision-history", help="Show decision revision/history view")
    p_decision_history.add_argument("decision_id")

    p_schema_status = sub.add_parser("schema-status", help="Show schema version status")
    p_capabilities = sub.add_parser("capabilities", help="Show runtime capabilities")
    p_vec_ready = sub.add_parser("sqlite-vec-readiness", help="Run sqlite-vec loader and readiness check")
    p_vec_states = sub.add_parser("vector-index-list", help="List vector index states")
    p_vec_states.add_argument("--object-type", choices=["episode", "semantic_node"])
    p_vec_states.add_argument("--vector-status")
    p_vec_states.add_argument("--limit", type=int, default=100)
    p_vec_sync_one = sub.add_parser("vector-index-sync", help="Refresh and sync one vectorized object")
    p_vec_sync_one.add_argument("object_type", choices=["episode", "semantic_node"])
    p_vec_sync_one.add_argument("object_id")
    p_vec_sync_one.add_argument("--force", action="store_true")
    p_vec_sync_batch = sub.add_parser("vector-index-sync-batch", help="Refresh and sync a batch of vectorized objects")
    p_vec_sync_batch.add_argument("--object-type", choices=["episode", "semantic_node"])
    p_vec_sync_batch.add_argument("--vector-status")
    p_vec_sync_batch.add_argument("--limit", type=int, default=100)
    p_vec_sync_batch.add_argument("--force", action="store_true")
    p_bench = sub.add_parser("retrieval-benchmark", help="Run local retrieval benchmark suite")
    p_bench.add_argument("--limit", type=int, default=5)
    p_explain = sub.add_parser("retrieval-explain", help="Explain ranked recall results for one query")
    p_explain.add_argument("query")
    p_explain.add_argument("--session-id")
    p_explain.add_argument("--limit", type=int, default=5)
    p_health = sub.add_parser("retrieval-health", help="Show retrieval/vector subsystem health summary")
    p_health.add_argument("--benchmark-limit", type=int, default=5)
    p_embed_ready = sub.add_parser("embedding-readiness", help="Check embedding runtime prerequisites without exposing secrets")
    p_doctor = sub.add_parser("doctor", help="Run a compact operator check for critical BrainOS runtime prerequisites")
    p_doctor.add_argument("--benchmark-limit", type=int, default=5)
    p_probe = sub.add_parser("real-corpus-probe", help="Run a small read-only real-corpus retrieval probe")
    p_probe.add_argument("--limit", type=int, default=5)
    p_ledger_verify = sub.add_parser("ledger-verify", help="Verify ledger integrity")
    p_ledger = sub.add_parser("ledger", help="Print ledger entries")

    return parser


def _sqlite_vec_error_payload(exc: SqliteVecReadinessError) -> dict[str, object]:
    return {
        "ok": False,
        "status": "warn",
        "error": str(exc),
        "error_kind": exc.error_kind,
        "detail": exc.detail,
        "action_hint": {
            "path_not_configured": "runtime_fix",
            "extension_load_failed": "runtime_fix",
            "readiness_probe_failed": "retry_or_runtime_fix",
        }.get(exc.error_kind, "inspect_error"),
    }


def _parse_bool_arg(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise BrainOSError("operator-call-required must be a boolean-like value")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    load_project_env(cwd=str(Path(args.db).resolve().parent), override=False)

    store = BrainOSStore(args.db, enable_vector=getattr(args, "enable_vector", False))
    try:
        if args.command == "init":
            store.initialize()
            print(f"Initialized {args.db}")
        elif args.command == "wm-set":
            store.initialize()
            event_id = store.set_working_memory(args.key, json.loads(args.value_json))
            print(event_id)
        elif args.command == "wm-get":
            store.initialize()
            value = store.get_working_memory(args.key)
            print(json.dumps(value, ensure_ascii=False, indent=2))
        elif args.command == "episode-add":
            store.initialize()
            metadata = json.loads(args.metadata_json)
            if args.kind and "kind" not in metadata:
                metadata["kind"] = args.kind
            if args.topic and "topic" not in metadata:
                metadata["topic"] = args.topic
            if args.source and "source" not in metadata:
                metadata["source"] = args.source
            episode_id = store.add_episode(
                session_id=args.session_id,
                content=args.content,
                metadata=metadata,
            )
            print(episode_id)
        elif args.command == "episodes-list":
            store.initialize()
            results = store.list_episodes(session_id=args.session_id, limit=args.limit)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif args.command == "consolidation-preview":
            store.initialize()
            print(json.dumps(store.preview_consolidation(args.episode_id), ensure_ascii=False, indent=2))
        elif args.command == "episode-promotion-get":
            store.initialize()
            promotion = store.get_episode_promotion(args.episode_id)
            if promotion is None:
                raise BrainOSError(f"episode promotion not found: {args.episode_id}")
            print(json.dumps(promotion, ensure_ascii=False, indent=2))
        elif args.command == "promote-episode":
            store.initialize()
            print(json.dumps(store.promote_episode(args.episode_id), ensure_ascii=False, indent=2))
        elif args.command == "episode-search":
            store.initialize()
            results = store.search_episodes_text(args.query, session_id=args.session_id, limit=args.limit)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif args.command == "recall":
            store.initialize()
            results = store.recall(args.query, session_id=args.session_id, limit=args.limit)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif args.command == "semantic-node-upsert":
            store.initialize()
            event_id = store.upsert_semantic_node(
                node_id=args.node_id,
                name=args.name,
                node_type=args.node_type,
                properties=json.loads(args.properties_json),
            )
            print(event_id)
        elif args.command == "semantic-node-get":
            store.initialize()
            node = store.get_semantic_node(args.node_id)
            if node is None:
                raise BrainOSError(f"semantic node not found: {args.node_id}")
            print(json.dumps(node, ensure_ascii=False, indent=2))
        elif args.command == "semantic-edge-upsert":
            store.initialize()
            event_id = store.upsert_semantic_edge(
                source_id=args.source_id,
                target_id=args.target_id,
                predicate=args.predicate,
                weight=args.weight,
            )
            print(event_id)
        elif args.command == "semantic-edges-list":
            store.initialize()
            print(json.dumps(store.list_semantic_edges(args.node_id, direction=args.direction), ensure_ascii=False, indent=2))
        elif args.command == "procedure-create":
            store.initialize()
            procedure_id = store.create_procedure(
                name=args.name,
                steps=json.loads(args.steps_json),
                description=args.description,
            )
            print(procedure_id)
        elif args.command == "procedure-list":
            store.initialize()
            print(json.dumps(store.list_procedures(active_only=not args.all, limit=args.limit), ensure_ascii=False, indent=2))
        elif args.command == "procedure-get":
            store.initialize()
            procedure = store.get_procedure(args.procedure_id)
            if procedure is None:
                raise BrainOSError(f"procedure not found: {args.procedure_id}")
            print(json.dumps(procedure, ensure_ascii=False, indent=2))
        elif args.command == "decision-log":
            store.initialize()
            decision = store.log_decision(
                decision_id=args.decision_id,
                question=args.question,
                status=args.status,
                recommended_option_id=args.recommended_option_id,
                operator_call_required=_parse_bool_arg(args.operator_call_required),
                options=json.loads(args.options_json),
                arguments=json.loads(args.arguments_json),
                counterarguments=json.loads(args.counterarguments_json),
                risks=json.loads(args.risks_json),
                missing_information=json.loads(args.missing_information_json),
                uncertainty_notes=json.loads(args.uncertainty_notes_json),
                metadata=json.loads(args.metadata_json),
                review_after=args.review_after,
            )
            print(json.dumps(decision, ensure_ascii=False, indent=2))
        elif args.command == "decision-list":
            store.initialize()
            print(json.dumps(store.list_decisions(status=args.status, limit=args.limit), ensure_ascii=False, indent=2))
        elif args.command == "decision-get":
            store.initialize()
            decision = store.get_decision(args.decision_id)
            if decision is None:
                raise BrainOSError(f"decision not found: {args.decision_id}")
            print(json.dumps(decision, ensure_ascii=False, indent=2))
        elif args.command == "inspect":
            store.initialize()
            print(json.dumps(store.inspect_object(args.object_type, args.object_id), ensure_ascii=False, indent=2))
        elif args.command == "decision-check":
            store.initialize()
            print(json.dumps(store.decision_check(args.decision_id), ensure_ascii=False, indent=2))
        elif args.command == "decision-history":
            store.initialize()
            print(json.dumps(store.decision_history(args.decision_id), ensure_ascii=False, indent=2))
        elif args.command == "schema-status":
            store.initialize()
            print(json.dumps(store.schema_status(), ensure_ascii=False, indent=2))
        elif args.command == "capabilities":
            store.initialize()
            print(json.dumps(store.capabilities(), ensure_ascii=False, indent=2))
        elif args.command == "sqlite-vec-readiness":
            try:
                store.initialize()
                print(json.dumps(store.sqlite_vec_readiness(), ensure_ascii=False, indent=2))
            except SqliteVecReadinessError as exc:
                print(json.dumps(_sqlite_vec_error_payload(exc), ensure_ascii=False, indent=2))
        elif args.command == "vector-index-list":
            store.initialize()
            print(json.dumps(store.list_vector_index_states(object_type=args.object_type, vector_status=args.vector_status, limit=args.limit), ensure_ascii=False, indent=2))
        elif args.command == "vector-index-sync":
            store.initialize()
            print(json.dumps(store.sync_vector_index(object_type=args.object_type, object_id=args.object_id, force=args.force), ensure_ascii=False, indent=2))
        elif args.command == "vector-index-sync-batch":
            store.initialize()
            print(json.dumps(store.sync_vector_index_batch(object_type=args.object_type, vector_status=args.vector_status, limit=args.limit, force=args.force), ensure_ascii=False, indent=2))
        elif args.command == "retrieval-benchmark":
            store.initialize()
            print(json.dumps(run_retrieval_benchmark(store, limit=args.limit), ensure_ascii=False, indent=2))
        elif args.command == "retrieval-explain":
            store.initialize()
            print(json.dumps(explain_recall(store, args.query, session_id=args.session_id, limit=args.limit), ensure_ascii=False, indent=2))
        elif args.command == "retrieval-health":
            store.initialize()
            print(json.dumps(retrieval_health_summary(store, benchmark_limit=args.benchmark_limit), ensure_ascii=False, indent=2))
        elif args.command == "embedding-readiness":
            store.initialize()
            print(json.dumps(embedding_readiness_summary(store), ensure_ascii=False, indent=2))
        elif args.command == "doctor":
            store.initialize()
            print(json.dumps(doctor_summary(store, benchmark_limit=args.benchmark_limit), ensure_ascii=False, indent=2))
        elif args.command == "real-corpus-probe":
            store.initialize()
            print(json.dumps(run_real_corpus_probe(store, limit=args.limit), ensure_ascii=False, indent=2))
        elif args.command == "ledger-verify":
            store.initialize()
            print(json.dumps(store.verify_ledger(), ensure_ascii=False, indent=2))
        elif args.command == "ledger":
            store.initialize()
            print(json.dumps(store.list_ledger(), ensure_ascii=False, indent=2))
        else:
            parser.error(f"Unknown command: {args.command}")
    except SqliteVecReadinessError as exc:
        print(json.dumps(_sqlite_vec_error_payload(exc), ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(2)
    except (BrainOSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(2)
    finally:
        store.close()


if __name__ == "__main__":
    main()
