# Resilience & Recovery Plan

## Layer 1 — GitHub Tags

| Tag | Point | Rollback command |
|---|---|---|
| `v0.1-foundation` | GitHub + Telegram + OneDrive + OpenRouter + DeepSeek + Gemini + local llama.cpp + prompt injection guard | `git checkout v0.1-foundation` |
| `v0.2-infra-stable` | + nightly backup + state export + resilience doc | `git checkout v0.2-infra-stable` |
| `v0.3-force-multipliers` | + weekly fireside cron + →wrong feedback loop + instant indexer + `correction-feedback-loop` skill | `git checkout v0.3-force-multipliers` |

Tags are pushed to `origin`. Recover with:

```bash
git fetch --tags
git checkout <tag-name>
```

## Layer 2 — Nightly Tarball Backups

**Schedule:** Daily at 23:00 UTC.

| Detail | Value |
|---|---|
| Script | `scripts/hermes-nightly-backup.py` |
| Local path | `/opt/data/backups/hermes-backup-YYYY-MM-DD.tar.gz` |
| OneDrive path | `OneDrive/Hermy/_backups/hermes-backup-YYYY-MM-DD.tar.gz` |
| Contents | config.yaml, .env, skills/, repo/docs, repo/scripts, session exports |
| Retention | 7 daily locally; OneDrive keeps indefinitely |

**Restore:**

```bash
tar -xzf /opt/data/backups/hermes-backup-YYYY-MM-DD.tar.gz -C /
```

Or download from OneDrive if local backup is gone.

## Layer 3 — State Export Protection

**Schedule:** Daily at 23:15 UTC.

| Detail | Value |
|---|---|
| Script | `scripts/hermes-nightly-state-export.py` |
| OneDrive path | `OneDrive/Hermy/_system/state-exports/YYYY-MM-DD/` |
| Contents | All `docs/state/*.md`, memory files, skill inventory |

**Restore:** Copy `.md` files back into the repo. No decompression needed.

## Layer 4 — Worker Queue

| Detail | Value |
|---|---|
| Queue folder | `OneDrive/Hermy/work-queue/` |
| Pattern | Write task file → worker polls → writes result file |
| Local SQLite | Planned as upgrade when volume exceeds ~100 tasks/day |

## Failure Scenarios

| Scenario | Recovery action | Time |
|---|---|---|
| Bad commit on main | `git revert HEAD` or checkout tag | ~2 min |
| Config corrupted | Restore config.yaml from nightly backup | ~5 min |
| .env secrets lost | Keys stored in backup tarball; restore .env only from there | ~5 min |
| State docs lost | Restore from OneDrive state export | ~5 min |
| Full server failure | New DO droplet → pull repo → restore backup tarball → restore state exports | ~30 min |
| GitHub deleted | Tarball has full `.git` dir; `git init` and `git remote add origin <new>` | ~15 min |
| Instant indexer daemon lost | `cd /opt/data/repo && source ~/.hermes/hybrid-env/bin/activate && nohup python3 scripts/hermy-instant-indexer.py --watch >> /opt/data/logs/instant-indexer.log 2>&1 &` — or let the watchdog cron restart it within 5 min | ~1 min |

## Service Inventory

| Service | Type | Managed by | Health check |
|---|---|---|---|
| Health monitor | Cron (every 6h) | `health-monitor` cron job | Reports to chat |
| Instant indexer | Daemon (30s poll) | `keep-instant-indexer-alive.sh` watchdog (every 5 min) | `ps aux | grep hermy-instant-indexer` |
| →wrong feedback | CLI script + 3am cron | `wrong.py` + herms-personal-time | `wrong.py list --unresolved` |
| Weekly Fireside | Cron (Fri 9am UTC) | `weekly-fireside` cron job | Delivers to chat each Friday |
| Token budget | Cron (daily 9am UTC) | `daily-token-budget` cron job | Reports to chat |
| Memory compression | Cron (daily 02:45 UTC) | `daily-memory-compression` cron job | Runs silently |

## Security Notes

- `.env` is included in backup tarballs. Store OneDrive backups securely.
- Test restore at least once before relying on it.
- Main branch protection (GitHub setting) prevents accidental force-pushes; enable it.
