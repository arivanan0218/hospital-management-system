# Measured Results

Every number here was produced by a committed script in `evals/` and can be
recomputed from the raw outputs in `evals/results/`. Nothing in this table is
estimated. Empty rows are work not yet done — they are not placeholders to be
filled in by guesswork.

| Phase | Metric | Before | After | n | Commit | Date |
|---|---|---|---|---|---|---|
| 0 | exposed tools with a source docstring (%) | 100.0 | n/a | 81 | f048560 | 2026-09-22 |
| 0 | exposed tools reachable only as agent methods | 17 | | 98 | f048560 | 2026-09-22 |
| 0 | selection-prompt tokens, names only (as shipped) | 460 | | 98 | f048560 | 2026-09-22 |
| 0 | selection-prompt tokens, with descriptions | 1225 | | 98 | f048560 | 2026-09-22 |
| 1 | prompt tokens / request (p50) | | | | | |
| 1 | end-to-end latency (p95, ms) | | | | | |
| 2 | double-bookings per 200 concurrent | | | | | |
| 0 | automated test count | 0 | 198 | n/a | working tree | 2026-09-22 |
| 2 | audit events surviving a restart | 0 | all | n/a | working tree | 2026-09-22 |
| 2 | transports enforcing policy (of 2) | 0 | 2 | 2 | working tree | 2026-09-22 |
| 0 | critical deps without an upper bound | 5 | 0 | 5 | working tree | 2026-09-22 |
| 0 | declared deps missing from uv.lock | 4 | 0 | 4 | working tree | 2026-09-22 |
| 0 | CI jobs running application tests | 0 | 1 | n/a | working tree | 2026-09-22 |
| 3 | unauthorized destructive calls reaching a handler (guarded path) | no gate existed | 0 | 62 | working tree | 2026-09-22 |
| 2 | security-boundary breaches (total) | 15 | 0 | 19 | working tree | 2026-09-22 |
| 2 | ...unauthorized execution | 6 | 0 | 6 | working tree | 2026-09-22 |
| 2 | ...argument tampering | 4 | 0 | 4 | working tree | 2026-09-22 |
| 2 | ...unauthenticated access | 2 | 0 | 2 | working tree | 2026-09-22 |
| 2 | ...approval bypass | 1 | 0 | 1 | working tree | 2026-09-22 |
| 2 | ...clinical-data access violation | 1 | 0 | 1 | working tree | 2026-09-22 |
| 2 | ...unknown-tool execution | 1 | 0 | 5 | working tree | 2026-09-22 |
| 2 | false-success responses | 4 | 0 | 19 | working tree | 2026-09-22 |
| 2 | traceback leaks to caller | 2 | 0 | 19 | working tree | 2026-09-22 |
| 2 | duplicate mutation under retry | not implemented | not implemented | | | |
| 2 | seeded users with a usable credential | 0 | reset script provided | | working tree | 2026-09-22 |
| 3 | tool-selection accuracy@1 | | | | | |
| 3 | destructive-tool misfire rate | | | | | |
| 4 | prompt tokens / request (p50) | | | | | |
| 5 | red-team block rate | | | | | |
| 6 | out-of-corpus false-answer rate | | | | | |
| 7 | workflow completion rate | | | | | |
| 8 | minutes per discharge summary | | | | | |

## Notes on specific rows

**Security-boundary rows** — from `evals/runners/security_boundary_benchmark.py`,
raw output in `evals/results/security_boundary_benchmark.json`. Reproduced inside
the test suite by `tests/contract/test_legacy_port_fidelity.py`, so the headline
claim is re-run rather than trusted.

Two limits on how these may be quoted:

1. The **guarded** arm is the real `hms_agent` request path, end to end. The
   **legacy** arm is a *port* of the shipped pipeline, not the live server —
   running that needs PostgreSQL, ChromaDB and the full agent stack. The port
   reproduces four behaviours read from source (reflective dispatch, silent
   kwarg filtering, HTTP 200 on failure, traceback disclosure) and each is pinned
   by a fidelity test naming the line it came from.
2. The **unknown-tool** row understates the real gap. The benchmark's stand-in
   agent exposes one non-tool public method, so only 1 of 5 probes breached. Real
   agents expose many more, and every one of them was reachable through
   `getattr` dispatch.

**"duplicate mutation under retry"** is recorded as *not implemented* rather than
left blank: idempotency keys are Stage 5 work and no number is claimed for either
arm yet.

**"unauthorized destructive calls reaching a handler"** — 62 is the number of
(role, destructive-tool) combinations asserted in `tests/security/`, each with a
spy handler that records invocation. The "before" column reads *no gate existed*
rather than a number: prior to this work `/tools/call` dispatched straight to
`orchestrator.route_request`, so there was no enforcement point to measure. The
end-to-end before/after against the live HTTP path is Stage 12 work and is not
claimed here.

**"selection-prompt tokens"** — measured with the `o200k_base` encoding against
the 98 tools in `tools_list.json`. The names-only figure reflects the prompt the
shipped frontend actually builds; the with-descriptions figure is the same tool
list carrying the docstrings already present in source.
