# NovaCourt runtime hotfix 10.2

## Incident and evidence

The manual run created a Zep container but showed no graph data, then a simulation call returned HTTP 429, and report generation logged missing headings followed by `ValueError`. These are independent paths. The historical graph failure's exact stage cannot be established from the available status-only log. The new stage, error type, and safe IDs will identify it during the repeat run. No live provider was called during development.

## Timeout and deadline map

| Layer | Setting/default | Limits | Terminates Court? | Scope |
| --- | --- | --- | --- | --- |
| HTTP POST/GET from MYKE | `fetch` has no explicit request timeout | One request, controlled by browser/abort | No; task thread persists. Explicit user cancellation calls `/cancel` | Request |
| Frontend status polling | Sequential GET, 1.5 s interval; after a failed GET, backoff 2/4/8/10 s, at most 5 consecutive failures | Observation only; no fixed total poll count | No; failed observation leaves backend running | Frontend task |
| Complete Court task | `NOVACOURT_TASK_TIMEOUT_SECONDS=1800` | Case, parallel Graph and Simulation, citations and finalization | Yes; after CaseResult, produces partial result | Court task |
| Graph operation | `NOVACOURT_GRAPH_TIMEOUT_SECONDS=600` | Create, ontology, send, processing, fetch | Graph branch only | Graph |
| Graph processing poll | `NOVACOURT_GRAPH_POLL_INTERVAL_SECONDS=3` | Delay between Zep episode status checks | No by itself | Graph operation |
| Graph materialization | `NOVACOURT_GRAPH_SETTLE_SECONDS=30`, clipped to graph deadline | Read after episodes processed, allowing indexing to appear | Can return explicit `empty` when complete with no relationships | Graph operation |
| Zep HTTP call | `NOVACOURT_PROVIDER_TIMEOUT_SECONDS=60` | Each Zep SDK request on the Court path | Branch may fail; not task deadline | Provider call |
| Simulation branch | `NOVACOURT_SIMULATION_TIMEOUT_SECONDS=600` | All three positions | Simulation branch only | Simulation |
| OpenAI call | `LLM_TIMEOUT_SECONDS=60`, clipped to remaining simulation/task time | One LangGraph model request | Eligible for bounded retry on transient error | Provider call |
| Court model retry | `NOVACOURT_PROVIDER_MAX_RETRIES=2`, `NOVACOURT_RETRY_MAX_DELAY_SECONDS=30` | 429, 5xx, connection/timeout; SDK retries disabled | No new call after cancellation/deadline | Per model request |
| Task cleanup | 24 hours, completed in-memory tasks only; persistent tasks exempt | Retention | Never cancels active Court | Task storage |
| Other pre-existing settings | `AUTH_TIMEOUT_SECONDS=5`, `PROVIDER_MAX_RETRIES=2`, report OpenAI SDK `max_retries=0` | Auth, non-Court LLM, report respectively | Indirectly through CaseResult only | Other provider calls |

All internal deadlines use `time.monotonic()`. The total Court clock begins in the backend worker. Graph and Simulation run concurrently and share its parent cancellation token; branch clocks are separate bounds and do not add serially. One provider HTTP timeout is not a complete job deadline. A remote in-flight call cannot be preempted; cancellation prevents the next call.

## Graph

`GraphBuilderService.create_graph`, `set_ontology`, `add_text_batches`, `_wait_for_episodes`, and `get_graph_data` are the installed API path. The installed Zep SDK returns a list of episodes from `graph.add_batch`. Court now checks that all episode IDs were acknowledged, polls their processing state with a monotonic deadline, and fetches nodes and edges after processing. A container alone never makes `ready`. A temporary empty fetch is retried within the materialization window. Completed processing with no nodes or no relationships after that window is `empty`, distinct from provider failure and timeout. The local canonical entities/relations are shown only when Zep extraction has both nodes and edges; they are not fabricated into Zep. The first snapshot remains `building` and is not terminal.

Safe graph logs carry case ID, graph ID, stage, elapsed/remaining milliseconds, provider status, HTTP status where exposed, and error type; no case content or provider body. Terminal metadata includes batch count, poll count, wait duration, stage and error type. Error codes include `GRAPH_TIMEOUT`, `GRAPH_INVALID_PAYLOAD`, and `GRAPH_PROVIDER_ERROR`. The graph builder uses no nonexistent synchronous build method. It does not recreate a graph on retry.

## Simulation and 429

The canonical route is `LegalDebateSimulator.simulate_prepared_case` → LangGraph nodes `position_a`, `position_b`, `judge` → `ChatOpenAI`. It does not use `llm_client`. LangGraph nodes own at most two retries after the original call; `ChatOpenAI` SDK retries are disabled. Retry applies to 429, temporary 5xx, connection errors and timeouts. 400/401/403 are not retried. `Retry-After` is honored but clipped to the configured maximum and remaining deadline; otherwise bounded exponential backoff is used. Cancellation is checked before each call and during each delay. Terminal logs and simulation metadata carry stage, retry count and `rate_limited` reason, without prompts or responses. Exhaustion leaves CaseResult and the independent Graph branch available and creates no substitute Judge.

## Report contract and partial results

The reproduced `ValueError` came from `case_service.py` raising `Report structure invalid` after `CaseReportService.generate_report` had already warned that optional headings were missing. The report now requires nonempty generated content, while the heading check creates a warning. `build_report_document` preserves heading-based sections when present and assembles one content section when headings are absent. The Court report is assembled deterministically from verified structured SimulationResult positions. If required decision content is missing, its section remains absent and the report is partial; no decision text is invented.

Finalization waits for both futures to become terminal. A branch failure or timeout does not discard the other branch or CaseResult. Status remains `processing` while either future runs. The frontend polls sequentially, recovers from transient GET failures, and detaching the view does not cancel the backend job. Explicit user cancellation still does. The Graph `empty` state and unavailable decision/report are presented separately from processing and failure. Existing repeated warning strings should be monitored in the manual retest.

If the global deadline expires before Court citation verification, the raw simulation is not published as `ready` and no unverified Judge decision is exposed. The already completed CaseResult and Graph remain in the partial result. Citation resolution starts only after a fresh deadline check.

## Verification

`test_novacourt_runtime_failures.py` contains 19 fake-provider tests for report validation and assembly, slow/empty/timeout/failing Graph, 429 success/exhaustion/no-retry/cancellation, branch wait order, citation deadline safety, and partial failure isolation. Full backend: 153 passing. Frontend: 32 passing. `compileall` and Vite build pass. `npm audit --audit-level=moderate`: 0 vulnerabilities. Providers were not contacted.

## Manual repeat of the same case

1. Start the backend and MYKE with the same configuration and submit the same case once. Record `task_id` and `case_id` without copying the case text into logs.
2. Watch status: POST returns quickly; GET stays `processing` while either Graph or Simulation is active; verify finalization only after both terminal states. Inspect `court_total_duration_ms`, branch durations, graph stage/batch/poll/wait metrics, simulation retry count and failed stage, and `court_report_status`.
3. In MYKE verify both positions, a real Judge decision, Court report with citations/sources, and visible graph. Confirm an unavailable section is explicit if a branch failed.
4. In backend logs verify there is no `Report structure invalid` ValueError, unhandled 429 or premature finalization. Inspect safe `graph_id`, stage and error type if Graph fails.
5. In Zep open that exact `graph_id`. Verify its container, processed episodes, nodes/entities and relationships/edges. “NovaCourt Legal Analysis” alone is insufficient. “No Graph Data Available” means runtime validation failed and the hotfix must remain a no-go for production closure.
