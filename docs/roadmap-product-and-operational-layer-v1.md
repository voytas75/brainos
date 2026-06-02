# BrainOS product roadmap v1

## Roadmap status
This document is planning-only for now.

Current mode:
- roadmap and prioritization only,
- no execution implied,
- no repo-facing documentation sync yet,
- no SSOT change for current runtime/retrieval scope.

Until execution starts on a specific slice:
- do not sync this roadmap into `README.md`, `docs/STATUS.md`, or other product-facing docs,
- treat README/STATUS updates as future closeout work attached to the relevant implementation slice,
- use this file as a parking/decision artifact, not as evidence that the product surface already exists.

## Goal
Przesunąć BrainOS z dobrze ugruntowanego storage-first memory core do codziennie używalnego narzędzia operacyjnego dla agentów i operatorów, bez psucia obecnego rdzenia:
- SQLite-first single-file storage
- layered memory model
- explicit promotion flow
- provenance / ledger verification
- operator-first health and readiness commands

## Confirmed current state
Potwierdzone na podstawie repo i live CLI:
- BrainOS ma działający CLI oparty o `argparse` w `src/brainos/cli.py`.
- Istnieją już komendy operator/runtime dla inicjalizacji, pamięci, retrieval, wektorów, explain, benchmarków i doctor.
- Repo jest uczciwie scoped jako local storage core, nie pełna runtime platforma (`README.md`).
- W `docs/STATUS.md` aktywny SSOT dotyczy retrieval/runtime slices; nie ma jeszcze repo-facing roadmapy dla warstwy produktowej/operacyjnej.
- W kodzie i testach nie ma dziś pierwszoklasowej warstwy `focus` / `decision` / `entity` / `blocker` / `wrap`.

## Decision
Budować cienką warstwę operacyjną nad obecnym core zamiast przebudowywać rdzeń albo kopiować 1:1 publiczny Brain OS MCP.

Status tej roadmapy:
- To jest dokument planistyczny / parking wykonawczy.
- Na tym etapie **nie** synchronizujemy jeszcze `README.md`, `docs/STATUS.md` ani innych repo-facing docs tylko po to, żeby ogłosić roadmapę.
- README/STATUS/docs closeout stają się zadaniem dopiero w momencie wejścia w wykonanie odpowiednich slice'ów.
- Sama obecność tej roadmapy nie zmienia jeszcze SSOT dla bieżącego runtime/retrieval scope.

Zasady:
1. Warstwa operacyjna ma mapować się na obecny model pamięci i ledger, nie tworzyć niezależnego, równoległego świata.
2. Każdy nowy slice ma mieć jawne CLI entry points, minimalny model danych, testy i README/docs closeout.
3. Najpierw wygrać codzienną używalność (`init`/`overview`/`focus`/`wrap`), dopiero potem szerszą integrację MCP/IDE.
4. Provenance, inspectability i operator discipline pozostają przewagą produktu; nie ukrywamy ich za „magicznym” UX.
5. Dopóki trwa wyłącznie etap roadmapy, repo-facing sync z README/STATUS pozostaje odroczony i nie jest wykonywany prewencyjnie.

## Decision-support boundary
Dla przyszłej warstwy `decision` obowiązuje kierunek product boundary:
- `decision` ma być **decision-support artifact**, nie auto-deciderem,
- BrainOS może rekomendować, ale nie powinien udawać finalnej autonomicznej decyzji,
- retrieval similarity i scoring są pomocnicze wobec jawnej argumentacji, constraints, ryzyk i brakujących danych,
- final choice pozostaje po stronie operatora.

Wszelkie przyszłe slice'y dla `decision` mają być zgodne z `docs/decision-support-contract-v1.md`.

### Decision-support non-goals v1
- brak autonomicznego finalnego wyboru za operatora,
- brak ukrytego policy engine udającego obiektywność,
- brak publicznego kontraktu opartego na jednym nieczytelnym score,
- brak automatycznego przejścia od rekomendacji do wykonania bez osobnego potwierdzenia,
- brak udawania, że podobieństwo retrieval samo w sobie rozwiązuje problem decyzyjny.

---

## Stage 1 — Product shell nad obecnym core

### Cel
Dać operatorowi i agentowi prosty first-run oraz codzienny punkt wejścia bez wymagania znajomości wszystkich niskopoziomowych komend.

### Slice 1.1 — `brainos init` product shell hardening
**Purpose**
Rozszerzyć istniejące `init`, żeby było pierwszą komendą produktową, nie tylko schema bootstrapem.

**Primary files**
- `src/brainos/cli.py`
- `src/brainos/store.py`
- `README.md`
- `tests/test_migration_and_cli.py`
- nowy test CLI, np. `tests/test_init_product_shell.py`

**Tasks**
- Zachować obecne `init`, ale dodać tryb outputu JSON-first lub czytelne post-init hints.
- Po `init` pokazać minimalne następne kroki: `overview`, `focus`, `doctor`.
- Uzgodnić, czy `init` opcjonalnie seeduje minimalne operational scaffolding (preferowane: nie seedować danych, tylko przygotować schema/views jeśli potrzebne).
- Dodać test na stabilny output i brak regresji starego zachowania.

**Validation**
- `uv run pytest -q tests/test_migration_and_cli.py tests/test_init_product_shell.py`
- `uv run brainos --db ./brain.db init`

**Done when**
- Nowy użytkownik po `init` dostaje jasny, stabilny next-step surface.
- Obecne flow schema bootstrap nie jest złamane.

### Slice 1.2 — `brainos overview`
**Purpose**
Wprowadzić jedną komendę statusową pokazującą wartość BrainOS na żywej bazie.

**Primary files**
- `src/brainos/cli.py`
- `src/brainos/store.py`
- ewentualnie nowy moduł `src/brainos/overview.py`
- `README.md`
- `tests/test_overview_cli.py`

**Tasks**
- Dodać komendę `overview` lub `status`.
- Zwracać zwarty JSON z:
  - db path,
  - schema status,
  - counts: episodes / semantic nodes / procedures / ledger entries,
  - retrieval/runtime summary,
  - recent activity summary,
  - placeholder na future operational state summary.
- Nie mieszać tego z `doctor`; `overview` ma odpowiadać na „co tu jest i w jakim stanie roboczym?”.

**Validation**
- `uv run pytest -q tests/test_overview_cli.py tests/test_json_cli_output.py`
- `uv run brainos --db ./brain.db overview`

**Done when**
- Jest jedna bezpieczna komenda statusowa dla codziennego użycia.
- Output jest stabilny, JSON-first i da się go później wystawić przez MCP.

### Slice 1.3 — README closeout for daily entry path
**Purpose**
Przepisać główny flow README z „storage core commands” na „daily entry path + deeper commands”.

**Primary files**
- `README.md`
- ewentualnie `docs/implementation-notes.md`

**Tasks**
- Dodać sekcję „Daily entry path”.
- Ustawić kolejność: `init` → `overview` → `doctor` → `focus`/`wrap` (gdy już istnieją).
- Zachować obecne niskopoziomowe przykłady, ale zepchnąć je niżej jako advanced commands.

**Validation**
- ręczny review README against real CLI commands

**Done when**
- README pokazuje BrainOS jako używalne narzędzie, nie tylko kolekcję primitives.

---

## Stage 2 — Operational state layer

### Cel
Dodać minimalny model operacyjny, którego użytkownik realnie potrzebuje na co dzień: decyzje, encje, blockery, plan, focus.

### Design rule
Nowe byty operacyjne nie zastępują obecnych warstw pamięci. Każdy byt ma:
- własny czytelny surface użytkowy,
- mapowanie do semantic/procedural/episodic/provenance,
- ledger event przy mutacji.

### Slice 2.1 — `decision` jako decision-support object
**Purpose**
Wprowadzić `decision` jako podstawowy byt operacyjny do wspierania decyzji operatora: framing pytania, pokazanie opcji, argumentów, ryzyk i niepewności.

**Boundary**
- `decision` nie jest autonomicznym chooserem,
- rekomendacja jest dozwolona,
- final choice pozostaje po stronie operatora,
- implementacja ma pozostać zgodna z `docs/decision-support-contract-v1.md`.

**Primary files**
- `src/brainos/schema.py`
- `src/brainos/store.py`
- `src/brainos/cli.py`
- nowy moduł np. `src/brainos/decisions.py`
- `tests/test_decision_cli.py`
- `README.md`
- `docs/implementation-notes.md`

**Tasks**
- Zaprojektować tabelę/model decision-support artifact z minimalnym zakresem:
  - `decision_id`
  - `question`
  - `status`
  - `recommended_option_id`
  - `operator_call_required`
  - `options_json`
  - `arguments_json`
  - `counterarguments_json`
  - `risks_json`
  - `missing_information_json`
  - `uncertainty_notes_json`
  - `review_trigger` lub `review_after`
  - `metadata_json`
  - timestamps
- Dodać CLI:
  - `decision-log`
  - `decision-list`
  - `decision-get`
- Każda mutacja ma pisać do ledgera.
- Powiązać decision-support artifact z semantic layer minimalnie przez metadata/ref ids albo dedykowany edge policy.
- Zachować jawny sygnał, że rekomendacja nie oznacza autonomicznego wyboru.

**Validation**
- `uv run pytest -q tests/test_decision_cli.py`
- smoke: `uv run brainos --db ./brain.db decision-log ...`

**Done when**
- Można jawnie zapisać i odczytać decision-support artifact z provenance.
- Output pokazuje pytanie, opcje, argumenty i niepewność.
- Final choice boundary pozostaje czytelna dla operatora.
- To nie rozwala istniejącego storage/retrieval flow.

### Slice 2.2 — `entity` / `initiative`
**Purpose**
Dać BrainOS byt roboczy reprezentujący projekt/obszar pracy.

**Primary files**
- `src/brainos/schema.py`
- `src/brainos/store.py`
- `src/brainos/cli.py`
- `tests/test_entity_cli.py`
- `README.md`

**Tasks**
- Dodać model encji z minimalnym zakresem:
  - `entity_id`
  - `name`
  - `kind`
  - `status`
  - `priority`
  - `current_summary`
  - `next_move`
  - `metadata_json`
- Dodać CLI:
  - `entity-upsert`
  - `entity-list`
  - `entity-get`
- Zachować możliwość późniejszego spinania z episodes/decisions/procedures.

**Validation**
- `uv run pytest -q tests/test_entity_cli.py`

**Done when**
- BrainOS potrafi pokazać podstawową jednostkę operacyjnego stanu.

### Slice 2.3 — `blocker`
**Purpose**
Dodać prosty model blockera zamiast ukrywania go wyłącznie w epizodach lub freeform metadata.

**Primary files**
- `src/brainos/schema.py`
- `src/brainos/store.py`
- `src/brainos/cli.py`
- `tests/test_blocker_cli.py`

**Tasks**
- Dodać model blockera:
  - `blocker_id`
  - `entity_id`
  - `severity`
  - `status`
  - `description`
  - `opened_at`
  - `resolved_at`
- CLI:
  - `blocker-open`
  - `blocker-resolve`
  - `blocker-list`
- Zaszyć ledger events i podstawowe validation rules.

**Validation**
- `uv run pytest -q tests/test_blocker_cli.py`

**Done when**
- BrainOS może odróżnić aktywny blocker od zwykłej notatki.

### Slice 2.4 — `plan`
**Purpose**
Wystawić procedural memory w prostszym, codziennym operacyjnym kształcie.

**Primary files**
- `src/brainos/store.py`
- `src/brainos/cli.py`
- ewentualnie `src/brainos/plans.py`
- `tests/test_plan_cli.py`

**Tasks**
- Na start oprzeć się na istniejących procedures zamiast tworzyć drugi silnik workflow.
- Dodać cienki UX:
  - `plan-set`
  - `plan-read`
  - `plan-advance`
- Zapewnić mapowanie plan step → procedure step / ledger event.

**Validation**
- `uv run pytest -q tests/test_plan_cli.py`

**Done when**
- Użytkownik ma prosty operacyjny plan surface bez utraty procedural-memory core.

---

## Stage 3 — Daily workflow commands

### Cel
Dać 3–4 komendy, które sklejają produkt w codzienny rytuał pracy.

### Slice 3.1 — `focus`
**Purpose**
Odpowiedzieć na pytanie „co teraz?” w jawny i debugowalny sposób.

**Primary files**
- `src/brainos/cli.py`
- nowy moduł `src/brainos/focus.py`
- `src/brainos/store.py`
- `tests/test_focus_cli.py`
- `README.md`

**Tasks**
- Dodać `focus` summary oparty początkowo na prostym scoringu:
  - entity priority
  - blocker severity
  - open plan step
  - staleness
  - recency of activity
- W outputcie pokazać nie tylko ranking, ale też `why` / `score_components`.
- Nie używać LLM-a; reguły mają być deterministic/debuggable.

**Validation**
- `uv run pytest -q tests/test_focus_cli.py`
- smoke on local fixture db

**Done when**
- BrainOS potrafi dać rekomendację next move z jawnym uzasadnieniem.

### Slice 3.2 — `wrap`
**Purpose**
Ustawić domknięcie sesji jako uporządkowaną operację, nie luźny zbiór zapisów.

**Primary files**
- `src/brainos/cli.py`
- nowy moduł `src/brainos/wrap.py`
- `src/brainos/store.py`
- `tests/test_wrap_cli.py`

**Tasks**
- Dodać `wrap` przyjmujące minimalny zestaw danych:
  - entity or session scope
  - what changed
  - next move
  - optional blocker
  - optional decision reference
- `wrap` ma tworzyć bounded writes do episodes + optional entity updates + ledger.
- Nie robić z tego od razu „AI summarizer”; najpierw structured write flow.

**Validation**
- `uv run pytest -q tests/test_wrap_cli.py`

**Done when**
- Jest stabilny session-close workflow z inspectable writes.

### Slice 3.3 — `inspect` / provenance drill-down
**Purpose**
Zamienić przewagę provenance na czytelny user-facing feature.

**Primary files**
- `src/brainos/cli.py`
- `src/brainos/store.py`
- `src/brainos/explain.py`
- `tests/test_inspect_cli.py`

**Tasks**
- Dodać `inspect` dla entity/decision/episode/plan item.
- Pokazywać:
  - source records,
  - related ledger events,
  - timestamps,
  - links do semantic/procedural refs jeśli istnieją.
- Spiąć to z istniejącą explain/retrieval surface tam, gdzie to ma sens.

**Validation**
- `uv run pytest -q tests/test_inspect_cli.py tests/test_explain_cli.py`

**Done when**
- Użytkownik może zobaczyć, skąd BrainOS „wie” daną rzecz.

---

## Stage 4 — Retrieval and decision trust layer

### Cel
Połączyć nową warstwę operacyjną z istniejącymi przewagami: explainability, retrieval discipline, provenance.

### Design rule
Warstwa trust ma wzmacniać jawność przesłanek, nie udawać autonomicznego strategic thinking.
Retrieval ma pomagać znaleźć evidence dla decyzji; nie może sam przez się stanowić finalnego rozstrzygnięcia.

### Slice 4.1 — decision conflict check v1
**Purpose**
Dodać prosty, nie-LLM-owy conflict check dla nowych decision-support artifacts.

**Primary files**
- `src/brainos/store.py`
- `src/brainos/cli.py`
- nowy moduł `src/brainos/decision_checks.py`
- `tests/test_decision_conflicts.py`

**Tasks**
- Regułowy check oparty o:
  - active/open decision artifacts,
  - shared entity links,
  - exact / lexical overlap na key fields,
  - status-based caution/conflict outcomes.
- CLI:
  - `decision-check`
- Wynik ma mieć klasy: `clear` / `caution` / `conflict` + evidence.

**Validation**
- `uv run pytest -q tests/test_decision_conflicts.py`

**Done when**
- BrainOS potrafi ostrzec o potencjalnym konflikcie bez marketingu o „AI strategic thinking”.

### Slice 4.2 — recall/explain for operational objects
**Purpose**
Sprawić, by `recall` i `retrieval-explain` umiały sensownie odnosić się do nowych obiektów operacyjnych.

**Primary files**
- `src/brainos/retrieval.py`
- `src/brainos/explain.py`
- `src/brainos/store.py`
- `tests/test_operational_recall.py`

**Tasks**
- Rozszerzyć recall/explain o entities/decisions/blockers/plans.
- Wyraźnie rozdzielić źródła:
  - episodic hit,
  - semantic hit,
  - operational object hit.
- Zaktualizować scoring/explain shape bez psucia obecnych retrieval contracts.
- Zachować interpretację, że retrieval/explain wspierają decision brief, a nie zastępują operator judgment.

**Validation**
- `uv run pytest -q tests/test_operational_recall.py tests/test_retrieval_eval.py tests/test_explain_cli.py`

**Done when**
- Nowa warstwa produktowa nie jest osobnym bytem odłączonym od retrieval core.
- Explain potrafi pokazać, skąd wzięły się argumenty dla rekomendacji.

### Slice 4.3 — decision-support evaluation contract
**Purpose**
Przestawić jakość warstwy `decision` z top-1 chooser accuracy na jakość briefu i jawność argumentacji.

**Primary files**
- nowy `docs/decision-support-contract-v1.md`
- `tests/test_decision_cli.py`
- ewentualne nowe fixtures/eval tests

**Tasks**
- Ustalić evaluation criteria dla decision support:
  - czy system pokazał sensowne opcje,
  - czy nie zgubił krytycznych constraints,
  - czy argumenty są oparte o evidence,
  - czy kontrargumenty i ryzyka są widoczne,
  - czy uncertainty jest pokazane uczciwie,
  - czy recommendation direction jest sensowny.
- Traktować top-1 choice tylko jako drugorzędny sygnał, nie główny kontrakt jakości.

**Validation**
- doc review
- future test alignment review

**Done when**
- Success dla decision layer nie jest już definiowany przez „czy system wybrał jedną opcję jak człowiek”.

---

## Stage 5 — MCP / agent integration

### Cel
Wystawić minimalną agent-native surface bez podporządkowywania całego projektu pod jednego klienta.

### Slice 5.1 — MCP surface v1
**Purpose**
Dodać mały zestaw narzędzi, które wystawiają nową warstwę operacyjną agentom.

**Primary files**
- nowy adapter / transport layer (path do decyzji po discovery)
- `README.md`
- nowy `docs/mcp-surface-v1.md`
- testy integracyjne adaptera

**Tasks**
- Najpierw discovery: wybrać minimalny adapter surface i sposób hostowania.
- Wystawić 5–7 narzędzi:
  - `focus_get`
  - `decision_log`
  - `decision_check`
  - `entity_get`
  - `entity_update`
  - `wrap_session`
  - `inspect_provenance`
- Zdefiniować JSON contracts i bounded errors.

**Validation**
- adapter-level integration tests
- manual smoke with one MCP client

**Done when**
- BrainOS da się podłączyć do klienta agentowego bez ręcznego klejenia niskopoziomowych komend.

### Slice 5.2 — agent instructions / daily protocol
**Purpose**
Dodać cienki protokół użycia dla agentów, ale nie uzależniać produktu od prompt magii.

**Primary files**
- nowy `docs/agent-protocol-v1.md`
- `README.md`
- ewentualne template files

**Tasks**
- Opisać kiedy agent ma czytać `focus`, `entity`, `decision`, `inspect`.
- Dodać minimalne snippets dla Claude/Cursor/MCP clients.
- Nie robić rozbudowanego slash-command frameworku przed walidacją MCP surface.

**Validation**
- doc review + one live smoke flow

**Done when**
- BrainOS ma lekki, repo-facing protokół użycia przez agentów.

---

## Stage 6 — Proof of value and positioning

### Cel
Udowodnić przewagę BrainOS na codziennych workflowach, nie tylko opisać architekturę.

### Slice 6.1 — product evidence scenarios
**Purpose**
Przygotować 2–3 scenariusze pokazujące operacyjną wartość.

**Primary files**
- nowy `docs/product-evidence-scenarios-v1.md`
- test/fixture support files
- `README.md`

**Tasks**
- Zdefiniować scenariusze:
  1. software project continuity
  2. research/project decision continuity
  3. long-running ops task with blockers
- Dla każdego pokazać:
  - initial state
  - daily commands used
  - why BrainOS gave useful continuity
  - inspect/provenance trail
- Zbierane metryki jakościowe:
  - fewer repeated decisions
  - better next-step continuity
  - inspectable source trail

**Validation**
- scenario walkthrough docs + reproducible fixture dbs

**Done when**
- Jest materiał pokazujący praktyczną przewagę produktu.

### Slice 6.2 — positioning refresh
**Purpose**
Zmienić framing z czysto technicznego na produktowy bez utraty prawdy.

**Primary files**
- `README.md`
- homepage/docs if applicable

**Tasks**
- Uzupełnić obecne techniczne zdanie o user-facing value proposition.
- Pozycjonować BrainOS jako:
  - durable operational memory,
  - inspectable provenance,
  - layered memory substrate,
  nie jako goły „AI OS”.
