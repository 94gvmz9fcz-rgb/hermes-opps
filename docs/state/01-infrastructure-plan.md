# Phase 1 Infrastructure Plan

## Goal

Create the bare-minimum operating layer that lets JStew and Hermy collaborate frequently, cheaply, and with high continuity.

Primary constraint: maximize useful collaboration while minimizing recurring API and cloud-compute spend without accepting quality loss.

## Recommended Framework

Use a hub-and-spoke model:

- **Telegram**: conversation and quick command surface.
- **GitHub repo**: durable, versioned operating state, decisions, skills, and technical docs.
- **OneDrive/Hermy**: active private shared workspace that Hermy can read/write through Microsoft Graph.
- **iCloud Drive**: Apple-native personal capture/staging layer; useful on-device but not the primary Hermy-readable backend.
- **iOS Shortcuts**: native capture buttons from iPhone/iPad into Telegram, OneDrive Inbox, or later webhook routes.
- **Hermes memory**: compact durable personal preferences and stable context.
- **Hermes skills**: reusable procedures for repeatable workflows.
- **Cloud Hermes runtime**: always-on executor for terminal, git, scheduled jobs, and integrations.

## Why This Framework

- It uses tools Josh already has: iPhone, iPad, iCloud, OneDrive, Telegram, GitHub.
- It avoids expensive always-on custom apps at the beginning.
- It keeps important state in plain Markdown, which is portable and cheap.
- It gives Hermy a real private read/write workspace through OneDrive while keeping public-ish operating docs in GitHub.
- It lets Hermy drive implementation in the repo while Josh provides device-side access and decisions.
- It supports future growth into iOS Shortcuts, Google Drive, webhooks, calendar/email, richer automations, or local models.

## Phase 1 Scope

### In Scope

1. State docs in `docs/state/`.
2. Repository Maintenance for commit/push/report workflows.
3. OneDrive/Hermy private shared workspace.
4. iCloud as optional Apple-side capture/staging.
5. First iOS Shortcuts plan.
6. Cost-control strategy.
7. Clear access checklist for Josh-provided setup.

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
  ├─ iCloud Drive/Hermy/ → optional Apple-side staging/capture
  └─ iOS Shortcuts → send notes/files/photos/tasks

Cloud Hermes Runtime
  ├─ Telegram gateway
  ├─ Microsoft Graph helper → OneDrive/Hermy private workspace
  ├─ Repo tools + git
  ├─ Memory + skills
  ├─ Cron/jobs later if needed
  └─ Optional webhooks later

OneDrive/Hermy
  ├─ _system/ → private workspace rules and verification files
  ├─ Inbox/ → raw private capture
  ├─ Notes/ Documents/ Projects/ Photos/
  └─ Exports/ Archive/

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
- `05-onedrive-workspace.md`: private workspace boundary and structure.
- `06-memory-first-cost-architecture.md`: retrieval-first cost architecture.

## Current Status

Phase 1 core bridge is active: Telegram, GitHub repo docs, Repository Maintenance, and OneDrive/Hermy private workspace are working.

## Next Action

Build the first iOS Shortcut intake path into Telegram or OneDrive/Hermy/Inbox, then document the working shortcut.
