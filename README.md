     1|# BrainOS
     2|
     3|BrainOS is a SQLite-first cognitive memory system for LLM agents.
     4|
     5|This repository contains the first local, production-oriented slice based on the BrainOS technical PDF: a deterministic single-file storage core with working, episodic, semantic, procedural, and provenance layers.
     6|
     7|## What this project is
     8|
     9|BrainOS stores multiple memory layers for an LLM agent inside a single SQLite database file.
    10|
    11|Current implementation provides:
    12|- working memory as JSON key/value state
    13|- episodic memory as session-scoped events
    14|- full-text search over episodes with FTS5
    15|- semantic memory as nodes and edges
    16|- procedural memory as JSON-defined procedures
    17|- consolidation preview and explicit promotion from episodes into semantic/procedural layers
    18|- promotion state tracking and duplicate-promotion protection
    19|- vector metadata lifecycle for native optional embedding support
    20|- an immutable ledger with chained hashes for provenance/audit
    21|
    22|The current repo is a **local storage core**, not a full runtime platform yet.
    23|
    24|## What problem it solves
    25|
    26|Instead of splitting agent memory across multiple services, BrainOS keeps the core memory model in one transactional SQLite file.
    27|
    28|That gives:
    29|- low infrastructure cost
    30|- deterministic local behavior
    31|- ACID transactions
    32|- simple portability
    33|- easy local development and testing
    34|
    35|## Current status
    36|
    37|Implemented now:
    38|- single-file SQLite database (`brain.db`)
    39|- WAL mode and foreign keys
    40|- JSON validation on JSON-bearing columns
    41|- `wm`
    42|- `episodes`
    43|- `episodes_fts`
    44|- `semantic_nodes`
    45|- `semantic_edges`
    46|- `procedures`
    47|- `ledger`
    48|- Python API
    49|- CLI
    50|- tests and smoke checks
    51|
    52|Not implemented yet:
    53|- vector storage/runtime integration beyond capability detection
    54|- hybrid retrieval orchestration (`FTS + vector + graph`)
    55|- full cognitive execution loop from the PDF
    56|- schema migrations beyond current hardening baseline
    57|- HTTP API
    58|
    59|## How it works
    60|
    61|BrainOS maps five memory areas into one SQLite database.
    62|
    63|### 1. Working memory
    64|Short-lived, current agent state.
    65|
    66|Table:
    67|- `wm`
    68|
    69|Use cases:
    70|- current mode
    71|- temporary state
    72|- active flags
    73|- local runtime context
    74|
    75|### 2. Episodic memory
    76|Append-style event memory for sessions.
    77|
    78|Tables:
    79|- `episodes`
    80|- `episodes_fts`
    81|
    82|Use cases:
    83|- interaction history
    84|- observations
    85|- logs worth recalling
    86|- searchable memory fragments
    87|
    88|### 3. Semantic memory
    89|Graph-like knowledge storage.
    90|
    91|Tables:
    92|- `semantic_nodes`
    93|- `semantic_edges`
    94|
    95|Use cases:
    96|- concepts
    97|- entities
    98|- facts
    99|- relations between concepts
   100|
   101|### 4. Procedural memory
   102|Structured procedures stored as JSON.
   103|
   104|Table:
   105|- `procedures`
   106|
   107|Use cases:
   108|- workflows
   109|- reusable agent routines
   110|- DAG-like step definitions
   111|
   112|### 5. Provenance / ledger
   113|Every meaningful write creates an auditable event.
   114|
   115|Table:
   116|- `ledger`
   117|
   118|Properties:
   119|- causal reference support
   120|- chained hashes
   121|- immutable event history for inspection
   122|
   123|## Architecture notes
   124|
   125|The attached PDF describes a strong target architecture, but the provided excerpt is incomplete in two important places:
   126|- the execution-flow section is cut off
   127|- `sqlite-vec` is mentioned, but operational details are incomplete in the excerpt
   128|
   129|So this repo intentionally implements the durable storage core first.
   130|
   131|One explicit implementation decision:
   132|- the PDF narrative implies cryptographic chaining, but the shown ledger DDL did not include an explicit link field
   133|- this implementation adds `previous_hash` to make the chain explicit and verifiable
   134|
   135|## Environment and tooling
   136|
   137|### Virtual environment
   138|Yes — this repo should use a local virtual environment managed by `uv`.
   139|
   140|Preferred workflow:
   141|- `uv sync --extra dev`
   142|- `uv run ...`
   143|
   144|### `.env`
   145|Yes — this repo now supports a project-local `.env` file.
   146|
   147|Current intent:
   148|- keep BrainOS runtime config project-scoped rather than shell-scoped
   149|- make operator checks and app runs behave consistently across interactive shells and OpenClaw exec
   150|- support local Azure embedding and sqlite-vec setup without relying on `~/.bashrc`
   151|
   152|Rules:
   153|- keep real secrets only in local `.env`, never in `.env.example`
   154|- shell env still overrides `.env`
   155|- `.env` is optional, but recommended for real local runs involving embeddings or sqlite-vec
   156|
   157|## How to run
   158|
   159|### 1. Install dependencies
   160|
   161|```bash
   162|uv sync --extra dev
   163|```
   164|
   165|### 2. Initialize the database
   166|
   167|```bash
   168|uv run brainos --db ./brain.db init
   169|```
   170|
   171|### 3. Write working memory
   172|
   173|```bash
   174|uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
   175|```
   176|
   177|### 4. Read working memory
   178|
   179|```bash
   180|uv run brainos --db ./brain.db wm-get agent_state
   181|```
   182|
   183|### 5. Add episodic memory
   184|
   185|```bash
   186|uv run brainos --db ./brain.db episode-add session-1 'Agent initialized successfully' --metadata-json '{"source":"manual"}'
   187|```
   188|
   189|### 6. Search episodic memory
   190|
   191|```bash
   192|uv run brainos --db ./brain.db episode-search Agent --limit 5
   193|```
   194|
   195|### 7. Preview consolidation candidate from an episode
   196|
   197|```bash
   198|uv run brainos --db ./brain.db consolidation-preview <episode-id>
   199|```
   200|
   201|### 8. Promote episode into semantic/procedural layer
   202|
   203|```bash
   204|uv run brainos --db ./brain.db promote-episode <episode-id>
   205|```
   206|
   207|### 9. Recall from episodic memory
   208|
   209|```bash
   210|uv run brainos --db ./brain.db recall Agent --session-id session-1 --limit 5
   211|```
   212|
   213|### 10. Create a semantic node
   214|
   215|```bash
   216|uv run brainos --db ./brain.db semantic-node-upsert n1 SQLite Concept --properties-json '{"kind":"database"}'
   217|```
   218|
   219|### 11. Create a semantic edge
   220|
   221|```bash
   222|uv run brainos --db ./brain.db semantic-edge-upsert n1 n2 RELATES_TO --weight 1.0
   223|```
   224|
   225|### 12. Create a procedure
   226|
   227|```bash
   228|uv run brainos --db ./brain.db procedure-create bootstrap '[{"step":"init-db"},{"step":"load-state"}]' --description 'Initialize BrainOS'
   229|```
   230|
   231|### 13. Check schema status
   232|
   233|```bash
   234|uv run brainos --db ./brain.db schema-status
   235|```
   236|
   237|### 14. Check runtime capabilities
   238|
   239|```bash
   240|uv run brainos --db ./brain.db capabilities
   241|```
   242|
   243|### 15. Verify ledger integrity
   244|
   245|```bash
   246|uv run brainos --db ./brain.db ledger-verify
   247|```
   248|
   249|### 16. Inspect ledger
   250|
   251|```bash
   252|uv run brainos --db ./brain.db ledger
   253|```
   254|
   255|## Diagnostic CLI contract (verified)

BrainOS now exposes operator-oriented diagnostic commands that prefer structured JSON over tracebacks.

Commands:
- `doctor`
- `retrieval-health`
- `embedding-readiness`
- `sqlite-vec-readiness`
- `capabilities`

### What to expect

- success path:
  - `status: "ok"` or `ok: true`
  - `action_hint: "noop"`
- degraded runtime path:
  - usually `status: "warn"`
  - sometimes `ok: false` on readiness-style commands
  - machine-readable fields such as `error_kind`, `detail`, `action_hint`
  - no need to parse traceback text for normal operator handling

### sqlite-vec runtime terminology

Two related surfaces are exposed intentionally:

1. Capability probe (`capabilities`)
- field: `sqlite_vec_runtime_origin`
- current values:
  - `explicit_path`
  - `disabled_without_explicit_path`
- meaning:
  - BrainOS capability probing only treats sqlite-vec as active when there is an explicit configured path
  - without explicit configuration, ambient probing is disabled on purpose

2. Env health (`embedding-readiness`, `doctor`, `retrieval-health`)
- field: `sqlite_vec_env.runtime_origin`
- current values:
  - `explicit_configured`
  - `ambient_detected`
  - `not_configured`
- field: `sqlite_vec_env.configured`
- meaning:
  - `configured = true` only for explicit intended configuration
  - `ambient_detected` means a foreign/runtime-inherited sqlite-vec path was seen, but BrainOS does not treat it as the intended active configuration

### How to read `recommended_fix` and `next_debug`

- `recommended_fix`
  - the most direct operator next move for the current degraded path
  - for sqlite-vec runtime issues this now points to:
    - `action_hint: "configure_sqlite_vec_path"`
    - `target: "BRAINOS_SQLITE_VEC_PATH"`
- `next_debug`
  - the next diagnostic handoff when the system has enough runtime to inspect retrieval quality
  - current retrieval benchmark failures point to `retrieval-explain`

### Example commands

```bash
uv run brainos --db ./brain.db capabilities
uv run brainos --db ./brain.db sqlite-vec-readiness
uv run brainos --db ./brain.db embedding-readiness
uv run brainos --db ./brain.db retrieval-health --benchmark-limit 5
uv run brainos --db ./brain.db doctor --benchmark-limit 5
```

## Typical local workflow
   256|
   257|```bash
   258|uv sync --extra dev
   259|uv run pytest tests/test_brainos.py -q
   260|uv run brainos --db ./brain.db init
   261|uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
   262|uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized' --metadata-json '{"source":"smoke"}'
   263|uv run brainos --db ./brain.db ledger
   264|```
   265|
   266|## Python usage
   267|
   268|Minimal example:
   269|
   270|```python
   271|from brainos import BrainOSStore
   272|
   273|store = BrainOSStore("brain.db")
   274|store.initialize()
   275|
   276|store.set_working_memory("agent_state", {"mode": "ready"})
   277|store.add_episode(
   278|    session_id="session-1",
   279|    content="Agent initialized successfully",
   280|    metadata={"source": "bootstrap"},
   281|)
   282|store.upsert_semantic_node(
   283|    node_id="n1",
   284|    name="SQLite",
   285|    node_type="Concept",
   286|    properties={"role": "storage"},
   287|)
   288|
   289|results = store.search_episodes_text("initialized")
   290|print(results)
   291|
   292|store.close()
   293|```
   294|
   295|## Main commands
   296|
   297|Available CLI commands:
   298|- `init`
   299|- `wm-set`
   300|- `wm-get`
   301|- `episode-add`
   302|- `episodes-list`
   303|- `consolidation-preview`
   304|- `episode-promotion-get`
   305|- `promote-episode`
   306|- `episode-search`
   307|- `recall`
   308|- `semantic-node-upsert`
   309|- `semantic-node-get`
   310|- `semantic-edge-upsert`
   311|- `semantic-edges-list`
   312|- `procedure-create`
   313|- `procedure-list`
   314|- `procedure-get`
   315|- `schema-status`
   316|- `capabilities`
   317|- `ledger-verify`
   318|- `ledger`
   319|
   320|Example:
   321|
   322|```bash
   323|uv run brainos --db ./brain.db init
   324|```
   325|
   326|## Project structure
   327|
   328|- `README.md` — main project description, how it works, how to run
   329|- `docs/api.md` — Python API and CLI reference
   330|- `docs/implementation-notes.md` — implementation decisions, spec gaps, next slice notes
   331|- `src/brainos/schema.py` — schema and initialization
   332|- `src/brainos/store.py` — storage API
   333|- `src/brainos/ledger.py` — canonical JSON + hash helpers
   334|- `src/brainos/cli.py` — CLI entrypoint
   335|- `tests/` — tests
   336|
   337|## Docs map
   338|
   339|Use docs this way:
   340|- start with `README.md` if you want to understand the project and run it
   341|- read `docs/api.md` if you want the exact API surface
   342|- read `docs/implementation-notes.md` if you want design tradeoffs and spec-gap notes
   343|
   344|## Design constraints
   345|
   346|What is solid already:
   347|- deterministic local persistence
   348|- transactional writes
   349|- audit-friendly ledger trail
   350|- simple Python integration
   351|- local testability
   352|
   353|What is intentionally deferred:
   354|- vector runtime bootstrapping
   355|- embedding integration
   356|- ranking fusion
   357|- graph traversal/retrieval API
   358|- procedure execution engine
   359|- network exposure
   360|
   361|## Development verification
   362|
   363|Run tests:
   364|
   365|```bash
   366|uv run pytest tests/test_brainos.py -q
   367|```
   368|
   369|Run a simple smoke path:
   370|
   371|```bash
   372|uv run brainos --db ./brain.db init
   373|uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
   374|uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized with WAL and ledger' --metadata-json '{"source":"smoke"}'
   375|uv run brainos --db ./brain.db episode-search BrainOS --limit 5
   376|uv run brainos --db ./brain.db ledger
   377|```
   378|
   379|## Roadmap
   380|
   381|Recommended next slice:
   382|1. add optional `sqlite-vec` capability detection and vector-table bootstrap
   383|2. define retrieval that combines FTS, vector similarity, and graph neighborhood
   384|3. add real schema migrations beyond current hardening baseline beyond v1 bootstrap
   385|4. formalize the cognitive execution loop
   386|5. optionally add a local HTTP API
   387|
   388|
   389|## Official smoke test
   390|
   391|Run the bounded end-to-end smoke test:
   392|
   393|```bash
   394|./scripts/e2e_smoke.sh
   395|```
   396|
   397|It writes a summary artifact to:
   398|- `artifacts/e2e-summary.json`
   399|
   400|
   401|## CLI error behavior
   402|
   403|For expected user-facing errors (for example not found, invalid promotion metadata, duplicate promotion), CLI exits with code `2` and returns a compact JSON error object on stderr.
   404|
   405|
   406|## Promotion audit
   407|
   408|To inspect whether a specific episode was already promoted:
   409|
   410|```bash
   411|uv run brainos --db ./brain.db episode-promotion-get <episode-id>
   412|```
   413|
   414|
   415|## Vector metadata status
   416|
   417|Current codebase now includes:
   418|- vector metadata lifecycle table
   419|- embedding profile contract surface
   420|- stale/missing tracking for embeddable objects
   421|
   422|It does **not** yet perform live embedding generation or vector retrieval.
   423|
   424|
   425|## Embedding execution adapter status
   426|
   427|Current code now includes a real LiteLLM-based embedding adapter boundary.
   428|
   429|What exists now:
   430|- logical embedding profile contract
   431|- environment-based Azure/LiteLLM resolution
   432|- execution path for episode embedding generation
   433|- vector metadata updates to `fresh` or `error`
   434|
   435|What is still not implemented:
   436|- batch refresh workflows
   437|- semantic-node embedding generation path
   438|- `sqlite-vec` retrieval integration
   439|
   440|
   441|## Azure embedding provider configuration
   442|
   443|BrainOS uses LiteLLM as the execution adapter for embeddings.
   444|Current operational target: Azure embeddings.
   445|
   446|Required environment variables:
   447|- `BRAINOS_EMBEDDING_MODEL` - model/deployment name passed to LiteLLM
   448|- `AZURE_API_BASE` - Azure OpenAI endpoint base URL
   449|- `AZURE_API_KEY` - Azure API key
   450|- `AZURE_API_VERSION` - Azure API version for embeddings
   451|
   452|Preferred project-local setup:
   453|- copy `.env.example` to `.env`
   454|- fill in real local values in `.env`
   455|
   456|Example `.env`:
   457|
   458|```dotenv
   459|BRAINOS_EMBEDDING_MODEL="azure/<your-embedding-deployment>"
   460|AZURE_API_BASE="https://<your-resource>.openai.azure.com"
   461|AZURE_API_KEY="..."
   462|AZURE_API_VERSION="2024-10-21"
   463|```
   464|
   465|Shell env still overrides `.env` when you need a temporary test override.
   466|
   467|Notes:
   468|- BrainOS keeps provider specifics out of domain logic.
   469|- `brainos-embedding-default` is the logical profile currently resolved through LiteLLM + Azure env config.
   470|- If `sqlite-vec` is unavailable, embedding execution may still succeed but vector storage is marked `disabled`.
   471|
   472|
   473|## sqlite-vec runtime configuration
   474|
   475|BrainOS can load `sqlite-vec` explicitly when the runtime does not expose `vec0` by default.
   476|
   477|Required env for runtime enablement:
   478|- `BRAINOS_SQLITE_VEC_PATH`
   479|
   480|Example `.env` value:
   481|
   482|```dotenv
   483|BRAINOS_SQLITE_VEC_PATH="/absolute/path/to/sqlite-vec/vec0.so"
   484|```
   485|
   486|Verification commands:
   487|
   488|```bash
   489|uv run brainos --db ./brain.db capabilities
   490|uv run brainos --db ./brain.db sqlite-vec-readiness
   491|```
   492|
   493|Expected healthy result:
   494|- `sqlite_vec: true`
   495|- `sqlite_vec_loaded: true`
   496|- readiness `ok: true`
   497|
   498|If `sqlite-vec-readiness` fails because `BRAINOS_SQLITE_VEC_PATH` is unset, treat that as a setup failure, not a generic retrieval failure.
   499|
   500|Current readiness failure classifications:
   501|