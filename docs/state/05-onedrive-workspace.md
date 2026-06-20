# OneDrive Workspace

## Status

Active. Hermy has verified Microsoft Graph access to Josh's OneDrive and can operate inside the private `OneDrive/Hermy/` workspace.

## Workspace Boundary

Hermy should treat `OneDrive/Hermy/` as the operating boundary.

Do not browse, modify, move, delete, or summarize content outside `OneDrive/Hermy/` unless Josh explicitly authorizes broader access for a specific task.

## Current Folder Structure

```text
OneDrive/Hermy/
  _system/
  Inbox/
  Notes/
  Photos/
  Documents/
  Projects/
  Exports/
  Archive/
```

## Folder Roles

- `_system/`: workspace rules, verification files, helper notes, and machine-readable operating docs.
- `Inbox/`: raw capture from Josh, Shortcuts, Telegram, or manual uploads.
- `Notes/`: processed private notes worth keeping.
- `Photos/`: selected images/photo intake Josh wants Hermy to process.
- `Documents/`: private documents shared for review, drafting, or extraction.
- `Projects/`: active private project materials.
- `Exports/`: outputs generated for Josh.
- `Archive/`: old or completed private items.

## Verified Files

Created by Hermy via Microsoft Graph:

```text
OneDrive/Hermy/_system/hello-from-hermy.md
OneDrive/Hermy/_system/workspace-rules.md
OneDrive/Hermy/Inbox/README.md
```

## Local Runtime Helper

A private helper script exists on the cloud runtime:

```text
/opt/data/home/.config/hermy/onedrive_graph.py
```

The OAuth token is stored privately at:

```text
/opt/data/home/.config/hermy/onedrive-token.json
```

Do not print token contents. Token handling should stay private.

## Operating Rules

1. Prefer creating new files or dated revisions over overwriting existing user content.
2. Do not delete or move Josh's files unless explicitly asked.
3. Use `Inbox/` for unprocessed items.
4. Promote items out of `Inbox/` only when Josh asks or an explicit workflow calls for it.
5. Keep durable operating state in GitHub repo docs, not only in OneDrive.
6. Keep personal/private content in OneDrive, not public or semi-public repo docs.

## Next Recommended Automation

Build iOS Shortcuts that send selected text/files/photos into either:

- Telegram for immediate action, or
- `OneDrive/Hermy/Inbox/` for private passive capture.
