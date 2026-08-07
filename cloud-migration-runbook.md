# Cloud Migration Runbook — STATUS: ✅ COMPLETE (2026-08-07)

**GitHub:** ✅ DONE — PAT configured via credential store (/root/.git-credentials, helper=store), hermes-opps + multi-market-pod pushed.
**OneDrive:** ✅ DONE — device-flow token (Files.ReadWrite.All), helper rebuilt at /opt/data/home/.config/hermy/, token in R2 backup manifest (never lose again). — AStew/JStew system
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
- `hunt_live_runner.sh` — `uv run` → `python3` (uv not installed on droplet → exit 127 on every run; deps already satisfied in cron runtime). Deployed + drift-audited.
- **TT fleet codebase RESTORED** — `/opt/data/project-tt/` was lost in migration (lived on Mac only); 9 files pulled from Mac `~/tt` via Funnel base64, git-committed. Weekly launchd agent verified loaded (next scan Sun 07:00).
- **Hardening (from gpt-5 adversarial scrub)**: UFW active (default deny incoming, SSH only), 6GB swap added + fstab, unattended-upgrades installed, Postgres verified localhost-only (scram).
- Model routing off OpenRouter (credits exhausted): CEO driver → deepseek-chat (jobs.json unpinned), compression → gpt-4o, titles → gpt-4o-mini, fallback → gpt-4o. Validated via fresh one-shot.

## OPEN ITEMS (Josh actions)
1. ~~OpenRouter weekly limit~~ — **RESOLVED by re-routing** (CEO → deepseek-chat, all aux → OpenAI). OpenRouter top-up now OPTIONAL: only needed to restore the claude-sonnet-4 CEO driver later.
2. **OneDrive re-auth** — device-code flow, fresh code minted per request (client 14d82eec-204b-4c2f-b7e8-296a70dab67e). On approval: rebuild helper at `/opt/data/home/.config/hermy/onedrive_graph.py` + token, resume inbox scan / cloud backup upload / session-history import.
3. **polymarket.us signing key** — `/opt/data/.polymarket-us-key` missing (intentionally excluded from backups). Needed only for account/order ops; regenerate from the polymarket.us portal if order-capable jobs return.
4. **GitHub push** — droplet deploy key generated (`/root/.ssh/github_deploy.pub`, comment hermes-droplet); add to `94gvm9zfc-rgb/hermes-opps` + `multi-market-pod` (Settings → Deploy keys) → then push tags/branches.
5. **Retire old droplet 157.230.163.72** — no DO API token on box; console steps: DO panel → droplet → Snapshots (create) → Destroy. (gpt-5 + AStew verdict: retire after snapshot; unknown state + no creds = liability.)
6. ~~Offsite backups~~ — **RESOLVED**: nightly tarball + state export → Cloudflare R2 `hermes-backups` (sigv4, no deps) + DO snapshot reminder (Sat 9am cron).
7. ~~Cloudflare R2 email pipeline~~ — **RESOLVED**: `.cf_config.json` recreated from skill reference (was lost with /opt/data/tmp); email check + bucket verified live.
8. **Session history** — droplet sessions DB is fresh; import from OneDrive state exports once (2) is done.

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
