# Cloud Migration Runbook — AStew/JStew system
**Status: CUTOVER COMPLETE — droplet is the sole Hermes home (2026-08-07).** Fleet re-enabled, pod drift-audited, backups verified.
**Droplet:** `ubuntu-s-2vcpu-4gb-amd-nyc1` / IP `134.122.21.188` / Ubuntu 24.04.4 LTS / 2vCPU / 3.8GB / 77GB

## Goal
Run Hermes + all crons + pod + fleet as a 24/7 always-on service, independent of Josh's Macs/home internet. Cloud is a temporary bridge to an owned home server.

## Infrastructure (DigitalOcean)
- **Droplet:** 2 vCPU / 4GB (`s-2vcpu-4gb-amd-nyc1`), NYC1, ~$24/mo
- **OS:** Ubuntu 24.04.4 LTS
- **Access:** root + `hermes` user via SSH key (id_ed25519 "digitalocean" on Mac)
- **Old droplet 157.230.163.72 still running (older setup, /opt/hermes-data era) — RETIRE to stop billing.**

## What's LIVE on the droplet (verified 2026-08-07)
- ✅ Hermes v0.20.0 gateway (systemd user service `hermes-gateway.service`, linger on)
- ✅ Telegram connected — **droplet owns the session (cutover done, source retired)**
- ✅ 46 cron jobs migrated; **14 data-writing jobs re-enabled after cutover** (all green; 4 fixed this session)
- ✅ Config `.env` (6 API keys), skills, scripts, pod, repo migrated
- ✅ kalshi-pod `deploy.sh` DRIFT AUDIT: PASS (28 scripts repo==deployed)
- ✅ Postgres 16.14 + pgvector installed (build-out, nothing consumes yet)
- ✅ Nightly backup + state export verified locally (`/opt/data/backups/hermes-backup-*.tar.gz`, 21MB)
- ✅ DO snapshot reminder cron (Sat 9am) added — Layer 4

## Fixed during cutover (2026-08-07)
- `pmus_paper_tracker.py` — was pointing at api.polymarket.us (trading host, needs signing key). Now reads **gateway.polymarket.us** (public read surface) via `requests` (urllib TLS-fingerprint → 403). Logs 30 teams/gaps daily.
- `polymarket_us_client.py` — `load_creds()`/`authed()` degrade gracefully when `/opt/data/.polymarket-us-key` missing (public reads keyless; order ops 401 loudly).
- `hermes-followup-checker.py` — module resolution now uses its own dir (`/opt/data/scripts`, where `hermes-followup.py` lives) instead of the dead `/opt/data/home/.hermes/scripts` path. Copies added to repo/scripts.
- `followup-checker` cron — stale workdir cleared.

## OPEN ITEMS (Josh actions)
1. **OpenRouter key weekly limit** — set to $10/wk, $0.70 left → `ceo-hourly-driver` (claude-sonnet-4) 402s. Raise limit to $25–50 at openrouter.ai/settings/keys (key ends ...188).
2. **OneDrive re-auth** — source container (hermes@5f8e422c75d2) is gone; onedrive_graph.py + token were lost with it. Device-code flow: https://login.microsoft.com/device (client 14d82eec-204b-4c2f-b7e8-296a70dab67e). Helper to be rebuilt at `/opt/data/home/.config/hermy/onedrive_graph.py`.
3. **polymarket.us signing key** — `/opt/data/.polymarket-us-key` missing (intentionally excluded from backups). Needed only for account/order ops; regenerate from the polymarket.us portal if order-capable jobs return.
4. **Retire old droplet 157.230.163.72** (and confirm source container is destroyed) — stop paying.
5. **Weekly DO snapshot** — reminder cron now handles it (Sat 9am).
6. **Session history** — droplet sessions DB is fresh (only post-cutover sessions). Historical context recoverable from OneDrive state exports once (2) is done.

## Migration data path (historical)
- Source box → droplet: `do_droplet_key` (pulled from Mac) → direct `scp`/`tar` over SSH
- Transferred: config.yaml, .env, .hermes/, scripts/, kalshi-pod/, repo/, skills/, cron/jobs.json
- NOT transferred (lost with source container): `/opt/data/home/.config/hermy/` (OneDrive helper+token), `/opt/data/.polymarket-us-key`, session history

## Files/scripts
- Pod: `/opt/data/kalshi-pod/` (deploy.sh has built-in DRIFT AUDIT)
- Fleet + cron scripts: `/opt/data/scripts/` (cron resolution root)
- Cron registry: `/opt/data/cron/jobs.json`
- Skills: `/opt/data/skills/`

## Rollback
- DO snapshot (weekly) → restore droplet. Source container is gone — rollback now means restoring from backup tarball + state export.

## Next steps
1. Josh: OpenRouter limit raise + OneDrive device-code approval (code handed in chat)
2. Rebuild onedrive_graph.py helper + verify inbox scan / backup upload
3. Retire old droplet 157.230.163.72
4. Owned-home-server bridge plan (exit path from cloud spend)
