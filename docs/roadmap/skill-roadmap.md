# Hermes Skill & System Roadmap

## Rule
Skills and systems are built only if they compound the AStew/JStew partnership's long-term usefulness.

## Legend
✅ Completed   ⬜ Not started   🟡 In progress   🚫 Deferred/cancelled

## Phase 1 — Foundation (Complete ✅)

| Item | Status | Notes |
|---|---|---|
| Memory System (persistent + session search) | ✅ | Working in-session, stores facts across turns |
| Personality & Communication Layer | ✅ | HERMS.md, Telegram channel, nicknames, comm rhythm locked |
| Telegram Control Channel | ✅ | Primary interface, active |
| GitHub Source of Truth | ✅ | Branch-only workflow, PRs, self-enforced protection |
| State Export Automation | ✅ | Nightly cron pushes to OneDrive |
| Backup System | ✅ | Local + OneDrive upload, 7-day rotation |
| EOL/Temp Pruning | ✅ | Baked into nightlies + repo-maintenance skill |
| Prompt Injection Guard | ✅ | Active, documented, protects against embedded instructions |
| OneDrive Workspace | ✅ | Microsoft Graph read/write, bounded to Hermy/ |
| Airtable CRM | ✅ | Base built, 110 contacts, fields set, enrichment pipeline works |
| Cost Governor Skill | ✅ | Exists — routes premium model usage |

## Phase 2 — Trust & Quality (Current)

| Item | Status | Notes |
|---|---|---|
| **Chex — Adversarial Review Agent** | ✅ Live | Spawns per substantial task. Reviews plans, watches build, monitors prod, escalates to JStew |
| Network Analyst — System Health | 🚫 Deferred | Shelved until Chex settles for a few days. Persistent 4h cron health monitor |
| Skill-Repo Audit Protocol | ✅ Baked | Every commit now checks: is every loaded skill in the repo? Commits missing ones. |

## Phase 3 — Convenience & Capture (Next Up)

| Item | Status | Notes |
|---|---|---|
| Voice Note → Action Pipeline | ⬜ | Drop a voice memo, I transcribe + extract actions. No typing. |
| Daily Brief / Digest | ⬜ | Morning cron: weather, calendar, who to ping, one priority. |
| Decision Capture → Searchable | ⬜ | Every decision auto-logged to decisions-log.md (already workflow, just tighten) |
| "Read My Mind" Intake | ⬜ | Drop a file/link/half-thought → I handle it without friction |
| Pull-Trigger Dashboard | ⬜ | Single Herms doc: active projects, recent decisions, next actions |

## Phase 4 — CRM Deepening (On Deck)

| Item | Status | Notes |
|---|---|---|
| Business Card Capture → OCR → Enrich | ⬜ | Snap a card, I get who they are, add to CRM |
| Phone Number Enrichment | ⬜ | Apollo cross-ref backfill |
| Daily "Who to Follow Up With" | ⬜ | Warm network maintenance |
| Drop-Folder Watch | ⚠️ Partially | OneDrive/Hermy exists but no auto-watch cron yet |

## Legacy Items (From Old Roadmap)

These were on the original roadmap and are either done, superseded, or no longer relevant:

| Old Item | Resolution |
|---|---|
| Architecture Review Board | Superseded by Chex. Chex IS the adversarial review. |
| Tailscale Secure Access | Deferred — not needed until we have a service to expose. |
| Capability Standard | Superseded — skills system + Chex review covers this. |
| External LLM Peer Review | Deferred — Chex fills this role internally. |
| Task System | Superseded — `todo` tool + cron + conversation works. |
| Tool execution sandbox | Hermes already provides one. |
| API adapters | Built as-needed (Airtable, OneDrive Graph). |
