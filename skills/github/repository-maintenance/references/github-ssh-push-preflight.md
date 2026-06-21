# GitHub SSH Push Preflight

Use this reference when Repository Maintenance needs to confirm that a repo can push non-interactively over SSH without modifying files.

## Goal

Verify three separate facts before claiming push access works:

1. The working tree is clean.
2. Local `main` is aligned with the tracked remote ref.
3. The configured push remote can authenticate and authorize a push.

## Read-only checks

From the repo root:

```bash
git status --short --branch
git status --porcelain
git remote -v
git remote get-url origin
git rev-parse HEAD
git rev-parse refs/remotes/origin/main 2>/dev/null || echo missing
```

`git status --porcelain` must be empty for a clean working tree.

## SSH alias checks

If the remote uses an SSH alias, for example:

```text
git@github-hermes-opps:OWNER/REPO.git
```

then `github-hermes-opps` is not a DNS hostname; it must be defined in SSH config. Confirm it resolves through SSH config before testing Git:

```bash
ssh -G github-hermes-opps | sed -n '1,40p'
ssh -T -o BatchMode=yes git@github-hermes-opps
```

If `ssh -G` or `ssh -T` says the hostname cannot be resolved, the fix is to create or restore the SSH config alias and its `IdentityFile`, not to change repository files.

## Remote authorization checks

Use read-only remote checks first:

```bash
git ls-remote --heads origin main
```

Then use a dry-run push to verify push authorization without modifying the remote:

```bash
git push --dry-run origin main
```

A successful `git ls-remote` proves fetch/read auth. A successful `git push --dry-run` is the safer signal for push/write auth.

Important nuances:

- `git rev-parse refs/remotes/origin/main` is only the locally cached tracking ref. If it matches `HEAD`, report that local `main` matches the local tracking ref; do **not** claim live remote alignment unless `git ls-remote --heads origin main` succeeds and returns the same hash.
- A direct `ssh -T git@github.com` test can fail even when Git operations through the configured repo remote succeed, because Git may be using repo/global SSH options, deploy-key mappings, or URL-specific configuration that the raw SSH command does not exercise. Treat `git push --dry-run origin main` as the decisive non-mutating push authorization check for Repository Maintenance. Report any raw SSH failure as a note, not as failure, if `git ls-remote` and `git push --dry-run` both succeed.

## SSH identity-file checks

If SSH auth fails with `Permission denied (publickey)` or `Identity file ... not accessible`, inspect the effective SSH config and key path without modifying files:

```bash
ssh -G github.com | grep -Ei '^(hostname|user|identityfile|identitiesonly) '
ssh -G <ssh-host-alias> | grep -Ei '^(hostname|user|identityfile|identitiesonly) '
```

Then check whether the configured `IdentityFile` exists and is readable by the current runtime user. Do not print private key contents.

Treat direct SSH probes as diagnostic context, not the final authority for repository push readiness. A direct command such as `ssh -T -o BatchMode=yes git@github.com` can fail while Git operations through the configured repository remote still succeed, depending on repo-specific SSH configuration or Git's invocation path. The final pass/fail signal for this skill is:

```bash
git ls-remote --heads origin main
git push --dry-run origin main
```

If both Git commands succeed, report SSH read/push access as working for the repo remote even if a direct `ssh -T` diagnostic failed; include the nuance in the final report.

Common durable diagnosis:

- Remote uses `git@github.com:OWNER/REPO.git`, but SSH config points `IdentityFile` at a path the current runtime cannot read, for example `/root/.ssh/...` while Hermes is running as another user.
- Treat this as a credential/configuration fix: move or recreate the deploy key under the runtime user's SSH directory, set permissions, and re-run `git ls-remote` plus `git push --dry-run` before claiming push access works.

## Reporting guidance

Report separately:

- Clean working tree: yes/no.
- Local/remote alignment: matching hash or ahead/behind state.
- SSH auth/read access: pass/fail and exact command used.
- Push authorization: pass/fail based on `git push --dry-run origin main`.

Do not say "SSH push access works" unless the dry-run push succeeds.