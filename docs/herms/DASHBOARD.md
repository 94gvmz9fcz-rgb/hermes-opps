# 🧭 Herms Dashboard

*Last updated: 2026-06-22*

---

## ⚡ Active

| What | Status | Started | Note |
|---|---|---|---|
| Read My Mind intake | ✅ Live | Today | Junk Drawer upgraded to universal capture-first pipeline |
| Airtable CRM | 🔄 Blocked — token permission | 06-21 | 110 contacts imported, needs Creator-level token to add fields |
| Siri Shortcut → Herms | 🔄 Built, untested | 06-21 | Shortcut setup guide ready, test pending |

---

## 📋 Next Up (Priority Order)

| # | Project | Why Now |
|---|---|---|
| 1 | **Unblock Airtable CRM** — add fields, re-import contacts, share invite | Core data infra for relationship management |
| 2 | **Test Siri Shortcut** — "Hey Siri, tell Herms..." voice pipeline | Low-hanging fruit, < 5 min |
| 3 | **Test Junk Drawer file pipeline** — drop a real file | Verify end-to-end before trusting daily use |
| 4 | **OpenRouter integration** — cheap model routing | Cost optimization after base infra stable |
| 5 | **Chex rollout** — adversarial review passes | Once collaboration protocol settles more |
| 6 | **Meta Glasses integration** | After Telegram pipeline rock-solid |

---

## 🧭 Recent Decisions

| Date | Decision |
|---|---|
| 06-22 | Read My Mind — universal capture-first intake pipeline |
| 06-22 | Image pipeline via EasyOCR + Junk Drawer shortcut |
| 06-22 | Decision capture format → formal schema + memory sync |
| 06-20 | Branch self-enforcement (free GitHub, no real rulesets) |
| 06-20 | OneDrive/Hermy as active shared workspace |
| 06-20 | OpenRouter before multi-provider setup |
| 06-20 | Cost control as first-class constraint |
| 06-19 | Telegram as primary chat surface |
| 06-19 | GitHub repo docs as durable state |

Full details: [decisions-log.md](../state/02-decisions-log.md)

---

## 🏗️ Pipeline Status

| Pipeline | Status | Last Action |
|---|---|---|
| **Junk Drawer** (file intake) | 🟢 Ready — needs test | `intake-webhook.py` running on :9999 |
| **Image OCR** | 🟢 Ready — needs test | `image-pipeline.py` committed, EasyOCR cached |
| **Siri → Herms** | 🟢 Setup done — needs test | Shortcut guide at `junk-drawer-setup.md` |
| **Cron: Nightly backup** | 🟢 Running | 23:00 UTC, saves to OneDrive |
| **Cron: State export** | 🟢 Running | 23:15 UTC |
| **Cron: Token tracker** | 🟢 Running | 09:00 UTC daily (commented: "just hermy") |
| **Cron: Morning standup** | 🟢 Running | 03:00 UTC |

---

## 📦 OneDrive/Hermy Layout

| Folder | Purpose | Contents |
|---|---|---|
| `Inbox/` | Files I've ingested, awaiting your action | Empty |
| `Read Later/` | Links saved for future follow-up | Empty |
| `Captures/` | Half-thoughts and fragments saved silently | Empty |
| `Junk Drawer/` | Raw dropped files (technical landing zone) | Empty |
| `Photos/` | Business cards, whiteboards, receipts | Empty |
| `Resources/` | Reference material (profile pics, shared assets) | Empty |
| `Backups/` | Cron-generated nightly state snapshots | Active |
| `Josh Stuff/` | Source exports, Apollo CSVs, resumes | CRM source data |

---

## 📊 Quick Status

| Check | Value |
|---|---|
| Memory usage | 99% — 2,179/2,200 chars |
| Repo branch | `main` (clean) |
| Open PRs | 0 |
| Pending cron jobs | 5 active |
| Skills loaded | collaboration-protocol, repository-maintenance, structured-evaluation-framework |
| Airtable base | `Jermy's CRM` — 110 contacts (Name + Notes only) |

---

*Dashboard auto-updates silently after significant interactions.*
*You check this when you wonder "what are we even doing."*
