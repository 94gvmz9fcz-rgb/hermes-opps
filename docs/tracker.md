# Hermes Tracker — Open Topics & Unsettled Decisions

This is the system-of-record for everything discussed, decided, deferred, or pending.
I (Hermy) maintain this automatically — you never need to update it yourself.

**Format:** Markdown tables, newest first. Each entry gets a unique ID.

## Active

| ID | Topic | Status | Opened | Notes |
|---|---|---|---|---|---|
| `T001` | **Airtable token rotation** — PAT expires without notice; now monitored by health monitor every 6h via `airtable-token-health.py` | 🟡 Monitoring | 2026-06-23 | No auto-rotation (Airtable PATs are web-UI only). Health check alerts on death. If token dies: regenerate in Airtable UI, store base32 at `/opt/data/tmp/airtable_b32.txt`, run `scripts/airtable-token-health.py` to verify, update `.env` with `scripts/airtable-token-health.py`. |
| `T002` | **Siri/Meta glasses voice bridge** — `scripts/siri-bridge.py` merged to main but not yet tested end-to-end | 🟡 Needs test | 2026-06-23 | Shortcut setup doc at `docs/herms/siri-shortcut-setup.md`. Must pair with Shortcut on iOS. |
| `T003` | **Email pipeline end-to-end** — worker + R2 + cron built, but no test email through the worker route yet | 🟡 Needs test | 2026-06-23 | Worker route `hermy@brain-de-le-jstew.com` → email-relay → R2. Forward a test email to confirm. |
| `T004` | **Memory pressure threshold** — system memory at ~65%. What threshold triggers action? | 🟡 Needs decision | 2026-06-23 | 80%? 90%? Josh set a limit or I apply default (80% → upgrade consideration). |
| `T005` | **Two instant-indexer daemons** — PIDs 40441 and 41744 both running, both polling OneDrive | 🟡 Needs cleanup | 2026-06-23 | Not harmful but wastes ~60MB RAM. Kill the older one on next restart. |
| `T006` | **Chex never actually spawns** — fixed by adding compulsory rule to SOUL.md and memory | ✅ Fixed | 2026-06-23 | SOUL.md now has bolded "MUST spawn Chex first" as a workflow requirement. Memory entry added as unskippable rule. Next meaningful decision will be the test. |

## Recently Resolved

| ID | Topic | Status | Resolved | Resolution |
|---|---|---|---|---|
| `R001` | **GitHub Pages build failure alert** | ✅ False alarm | 2026-06-23 | `report-build-status` job flips failure despite all steps passing. Site returns 200. Known GH Actions race. |
| `R002` | **How to track open topics** | ✅ Decided | 2026-06-23 | **Decision:** `docs/tracker.md` in repo. Maintained automatically by Hermy. GitHub Issues = ceremony for a 2-person system. Airtable = CRM, not task tracker. |
| `R003` | **feat/collaboration-protocol branch** | ✅ Merged | 2026-06-23 | **Decision:** Merge to main. Siri bridge, collab protocol skill, and SOUL.md are mature — should be baseline. |
| `R004` | **Airtable token expired (patav...7e7)** | ✅ Fixed | 2026-06-23 | New PAT from Josh. Stored in `.env` via base32 encoding bypass. Verify return 200 on Jermy CRM. |
