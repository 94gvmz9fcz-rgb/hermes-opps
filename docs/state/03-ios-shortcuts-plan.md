# iOS Shortcuts Plan

## Goal

Use iOS Shortcuts to turn Josh's iPhone and iPad into low-friction capture and command surfaces for Hermy.

The first shortcuts should be simple, native, cheap, and easy to inspect.

## Recommended First Shortcuts

### 1. Send Note to Hermy

**Purpose:** Capture a thought, task, idea, or instruction from iPhone/iPad.

**Input:** Text entered through Shortcut prompt or Share Sheet.

**Output:** Sends text to Hermy through Telegram, or later to a webhook if configured.

**Why first:** It is the simplest high-value bridge between Josh's devices and Hermy.

### 2. Send File to Hermy

**Purpose:** Share a file from iCloud Drive, Files, Photos, or another app.

**Input:** File via Share Sheet.

**Output:** Sends the file to Telegram chat with Hermy, or stores it in `iCloud Drive/Hermy/Inbox/` for later processing.

**Why second:** Gives Hermy access to specific files without broad device access.

### 3. Save to Hermy Inbox

**Purpose:** Save content locally first without requiring immediate Hermy processing.

**Input:** Text, file, photo, PDF, or URL.

**Output:** Saves into an iCloud folder such as:

```text
iCloud Drive/Hermy/Inbox/
```

**Why third:** Cheap, reliable capture that does not require an API call every time.

### 4. Daily Check-In

**Purpose:** Start a lightweight daily reflection or planning message.

**Input:** Prompted answers from Josh.

**Output:** Sends structured note to Hermy or saves it to iCloud Inbox.

**Why later:** Useful after basic capture works.

## Proposed iCloud Folder Structure

```text
iCloud Drive/Hermy/
  Inbox/
  Notes/
  Photos/
  Documents/
  Projects/
  Exports/
  Archive/
```

## Routing Rules

- Use Telegram for immediate conversation or action.
- Use iCloud Inbox for passive capture.
- Use GitHub repo docs for durable operating state, decisions, plans, and workflows.
- Use OneDrive/Google Drive only when the content naturally lives there or a workflow requires it.

## Low-Cost Design

To minimize spend:

- Do not send every capture to the LLM immediately.
- Batch passive captures from iCloud Inbox into summaries later.
- Use filenames and folders as lightweight metadata.
- Use manual Josh-triggered processing before adding scheduled automation.

## Information Needed From Josh

1. Confirm the iCloud folder name: default `Hermy`.
2. Confirm whether Telegram should receive shortcut outputs first.
3. Confirm whether Shortcuts should prefer:
   - immediate send to Hermy, or
   - save to iCloud Inbox for later processing.
4. Send screenshots/export details once the first Shortcut is created, so Hermy can document and improve it.

## First Build Recommendation

Start with **Send Note to Hermy**:

1. Shortcut asks for text.
2. Shortcut sends the text to the Telegram chat with Hermy.
3. Josh confirms Hermy receives it.
4. Hermy documents the working shortcut and creates the next one.
