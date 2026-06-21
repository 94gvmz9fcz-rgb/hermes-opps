# 🧭 Herms Dashboard

*Last updated: 2026-06-22*

---

## ⚡ Active

| What | Status | Started | Note |
|---|---|---|---|
| Read My Mind intake | ✅ Live | 06-22 | Universal capture-first pipeline active |
| Hybrid Architecture (local offload) | ✅ LIVE | 06-22 | ChromaDB seeded, query bridge works, hourly indexer, →local command |
| Airtable CRM | 🟢 Ready — token live, 16 fields set | 06-21 | Awaiting Josh's black book data |
| Memory compression cron | ✅ Live | 06-22 | 02:45 UTC daily |
| Work brain — Phase 1 & 2 | 🟢 Built | 06-22 | `docs/josh/` — 5 docs |
| Siri Shortcut → Herms | 🔄 Untested | 06-21 | Guide ready

---

## 📋 Next Up (Priority Order)

| # | Project | Why Now |
|---|---|---|
| 1 | **CRM data re-import** — map 110 contacts to fields, generate invite link | Last blocking item before CRM operational |
| 2 | **Test Siri Shortcut** — "Hey Siri, tell Herms..." voice pipeline | < 5 min, Josh does when near phone |
| 3 | **Test Junk Drawer file pipeline** — drop a real file | Verify end-to-end before daily use |
| 4 | **OpenRouter integration** — cheap model routing | Cost optimization after base infra stable |
| 5 | **Chex rollout** — adversarial review passes | Once core infra settled |
| 6 | **Meta Glasses integration** | After Telegram pipeline rock-solid |

---

## 🧭 Recent Decisions

| Date | Decision |
|---|---|
| 06-22 | Memory → navigation pointers + daily compression cron at 02:45 UTC |
| 06-22 | Decision log enriched: journal format with daily entries |
| 06-22 | Weekly health checks established (memory %, cron success, disk) |
| 06-22 | Read My Mind — universal capture-first intake pipeline |
| 06-22 | Image pipeline via EasyOCR + Junk Drawer shortcut |
| 06-22 | Herms Dashboard — personal operating layer home base |
| 06-20 | Branch self-enforcement (free GitHub, no real rulesets) |
| 06-20 | OneDrive/Hermy as active shared workspace |
| 06-20 | Cost control as first-class constraint |
| 06-19 | Telegram as primary chat surface |

Full details and daily journals: [decisions-log.md](../state/02-decisions-log.md)

---

## 🏗️ Pipeline Status

| Pipeline | Status | Last Action |
|---|---|---|
| **Junk Drawer** (file intake) | 🟢 Ready — needs test | `intake-webhook.py` running on :9999 |
| **Image OCR** | 🟢 Ready — needs test | `image-pipeline.py` committed, EasyOCR cached |
| **Siri → Herms** | 🟢 Setup done — needs test | Shortcut guide at `junk-drawer-setup.md` |
| **Memory compression** | 🟢 Running | 02:45 UTC daily |
| **Cron: Nightly backup** | 🟢 Running | 23:00 UTC, saves to OneDrive |
| **Cron: State export** | 🟢 Running | 23:15 UTC |
| **Cron: Token tracker** | 🟢 Running | 09:00 UTC daily (commented: "just hermy") |
| **Cron: Morning standup** | 🟢 Running | 03:00 UTC |

---

## 📦 OneDrive/Hermy Layout

| Folder | Purpose | Contents |
|---|---|---|
| `Inbox/` | Files ingested, awaiting your action | Empty |
| `Read Later/` | Links saved for future follow-up | Empty |
| `Captures/` | Half-thoughts captured silently | Empty |
| `Junk Drawer/` | Raw dropped files (technical landing zone) | Empty |
| `Photos/` | Business cards, whiteboards, receipts | Empty |
| `Resources/` | Reference material (profile pics, shared assets) | Empty |
| `Backups/` | Cron-generated nightly state snapshots | Active |
| `Josh Stuff/` | Source exports, Apollo CSVs, resumes | CRM source data |

---

## 📊 Quick Status

| Check | Value |
|---|---|
| Memory usage | **45%** — 990/2,200 chars (down from 95%) |
| Memory compression | Auto at 02:45 UTC daily, triggers at 60%+ |
| Decision log | Enriched with journal format + Foundation Day entry |
| Repo branch | `main` (clean) |
| Open PRs | 0 |
| Active crons | 6 (new: memory compression) |
| Skills loaded | collaboration-protocol, repository-maintenance, structured-evaluation-framework |
| Airtable base | `app6l2hwxinBLwHCa (Untitled)` — 16 fields, token live |
| Health check | Weekly auto-monitor active — flags at 85% memory or threshold breach |

---

## 🩺 Health Monitor

| Check | Threshold | Current | Status |
|---|---|---|---|
| Memory | < 85% | 45% | ✅ |
| Crons | All running | 7 active | ✅ |
| Hybrid DB | Running | 42 chunks, 6 files | ✅ |
| Token budget | Monthly limit | Tracking | ✅ |
| Disk | < 90% | TBD | ⏳ |

*Weekly health check runs automatically. I flag proactively when any metric crosses a threshold.*

---

*Dashboard auto-updates silently after significant interactions.*
*Bookmark this — it's your 10-second "what are we even doing" answer.*
