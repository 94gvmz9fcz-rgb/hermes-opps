# Phase 1 Infrastructure Plan

## Goal

Create the bare-minimum operating layer that lets JStew and Hermy collaborate frequently, cheaply, and with high continuity.

Primary constraint: maximize useful collaboration while minimizing recurring API and cloud-compute spend without accepting quality loss.

## Recommended Framework

Use a hub-and-spoke model:

- **Telegram**: conversation and quick command surface.
- **GitHub repo**: durable, versioned operating state, decisions, skills, and technical docs.
- **iCloud Drive**: first personal capture/storage layer because Josh primarily uses Apple hardware.
- **iOS Shortcuts**: native capture buttons from iPhone/iPad into Telegram, repo intake, or later webhook routes.
- **Hermes memory**: compact durable personal preferences and stable context.
- **Hermes skills**: reusable procedures for repeatable workflows.
- **Cloud Hermes runtime**: always-on executor for terminal, git, scheduled jobs, and integrations.

## Why This Framework

- It uses tools Josh already has: iPhone, iPad, iCloud, Telegram, GitHub.
- It avoids expensive always-on custom apps at the beginning.
- It keeps important state in plain Markdown, which is portable and cheap.
- It lets Hermy drive implementation in the repo while Josh provides device-side access and decisions.
- It supports future growth into OneDrive, Google Drive, webhooks, calendar/email, richer automations, or local models.

## Phase 1 Scope

### In Scope

1. State docs in `docs/state/`.
2. Repository Maintenance for commit/push/report workflows.
3. iCloud folder convention for capture.
4. First iOS Shortcuts plan.
5. Cost-control strategy.
6. Clear access checklist for Josh-provided setup.

### Out of Scope For Now

- Full custom mobile app.
- Complex multi-cloud sync.
- Paid automation platforms unless justified.
- Heavy always-on background agents beyond Hermes/Gateway.
- Personality/identity deep dive until minimum infrastructure is stable.

## Proposed Architecture

```text
iPhone / iPad
  ├─ Telegram → Hermy conversation + commands
  ├─ iCloud Drive/Hermy/ → personal capture files
  └─ iOS Shortcuts → send notes/files/photos/tasks

Cloud Hermes Runtime
  ├─ Telegram gateway
  ├─ Repo tools + git
  ├─ Memory + skills
  ├─ Cron/jobs later if needed
  └─ Optional webhooks later

GitHub Repo
  ├─ docs/state/ → shared operating state
  ├─ docs/decisions/ or decisions log → durable decisions
  ├─ skills/capabilities → repeatable workflows
  └─ scripts/templates later
```

## Minimum Access Josh May Need To Provide

- Confirm desired iCloud Drive top folder name. Default: `Hermy`.
- Confirm whether Telegram remains the primary chat interface for now.
- Provide screenshots or exported Shortcut definitions when building iOS Shortcuts.
- Approve any token/API credentials before they are stored or used.
- Confirm whether OneDrive/Google Drive should be delayed until a real need appears.

## Operating Rules

- Prefer Markdown docs and repo commits over hidden state.
- Prefer iOS-native tools before paid SaaS.
- Prefer open-source tools before paid cloud services.
- Use expensive model calls selectively for high-leverage reasoning, not routine capture.
- Summarize and cache context before reusing it.
- Ask Josh only for decisions or access that Hermy cannot infer or safely perform.

## Initial Deliverables

- `00-jstew-hermy-home.md`: shared home base.
- `01-infrastructure-plan.md`: this file.
- `02-decisions-log.md`: durable decisions.
- `03-ios-shortcuts-plan.md`: device-side automation plan.
- `04-cost-control-strategy.md`: rules for keeping spend low without quality loss.

## Next Action

Create the Phase 1 docs, then use Repository Maintenance to review, commit, push, and report the commit hash.
