# Disaster Recovery Runbook — droplet restore in under 30 minutes

**Target:** `ubuntu-s-2vcpu-4gb-amd-nyc1` (134.122.21.188) · **Last verified:** 2026-08-07 (restore drill PASS)

## What's protected and where
| Asset | Location |
|---|---|
| Nightly tarball (config.yaml, .env, skills, repo, .hermes, kalshi-pod + ledgers, exports incl. hybrid-db.sql) | **R2 `hermes-backups`** (S3 API) + local `/opt/data/backups/` (7-day) |
| State exports (memory/skill inventory) | R2 + `/opt/data/exports/` |
| Postgres `hybrid` DB | `hybrid-db.sql` inside the tarball (pg_dump) |
| Git repos | Local git + pending GitHub push (deploy key ready) |

## Restore procedure (fresh droplet, same size)
1. **Provision:** DO console → new Ubuntu 24.04 droplet (2vCPU/4GB). Add our SSH key.
2. **Base install:** `apt update && apt install -y python3 python3-pip postgresql postgresql-16-pgvector docker.io` (or Docker per playbook). Start Postgres.
3. **Get the tarball** (S3 API — NOT the v4 GET, which can serve a stale edge cache):
   ```bash
   # sigv4 GET via /opt/data/scripts/r2_upload.py's sibling (or boto3 with R2 keys from /opt/data/tmp/.r2keys.env)
   # keys live in /opt/data/tmp/.cf_config.json (account) + .r2keys.env (R2 S3 keys)
   ```
   Verify: `sha256sum` of the R2 object must match the local tarball if one exists.
4. **Extract to /opt/data:** `mkdir -p /opt/data && tar -xzf hermes-backup-<date>.tar.gz -C /opt/data`
   → restores config.yaml, .env, skills/, repo/, kalshi-pod/ (ledgers!), .hermes/ (memory), exports/.
5. **Postgres:** `su postgres -c "psql -c 'CREATE DATABASE hybrid;'" && psql -d hybrid < exports/hybrid-db.sql` + `CREATE EXTENSION vector` if missing.
6. **Cron registry:** `/opt/data/cron/jobs.json` — restore from R2 tarball if not present (it lives under /opt/data — add to tarball paths if missing) or re-create from the repo's backup copies.
7. **Gateway:** install Hermes (same version), `hermes config migrate` if needed, then `systemctl --user enable --now hermes-gateway` (linger on).
8. **Verify:** `hermes chat -q "Reply OK"` exit 0 · Telegram connects · `job-lag-monitor` silent · watchdog silent-exit test · run `./deploy.sh` in kalshi-pod (drift audit PASS).
9. **Secrets to rehydrate manually** (never in tarball): `.polymarket-us-key` (KYC portal), GitHub deploy key (add new key to repos), OneDrive token (device-code once), OpenRouter key (optional).

## Known gaps (be honest on restore)
- `/opt/data/cron/jobs.json` is NOT in the tarball paths yet — add `os.path.join(HOME_DIR, "cron")` to `hermes-nightly-backup.py` paths (small patch, next backup cycle).
- Hybrid DB is a 1-row foundation; full pgvector migration of the index is future work.

## Test cadence
- Weekly: `python3 /opt/data/scripts/r2_upload.py --prune` (also verifies R2 access).
- Monthly: full drill — download → sha → extract → spot-check config.yaml + track_record.jsonl + memory.md.
- The 2026-08-07 drill caught the backup manifest missing config/kalshi-pod/.hermes — FIXED and re-verified. Don't let a manifest edit regress this silently: the restore drill is the test.
