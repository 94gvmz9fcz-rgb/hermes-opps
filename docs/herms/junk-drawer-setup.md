# 🗂️ Junk Drawer — The Universal Intake

**One pipeline. Three input types.** All thought → Herms, no friction.

```
You do something
        ↓
It arrives in this chat
        ↓
I capture by default → ask one question → act on your reply
```

**Capture is the default.** Nothing is ever lost. Processing is a second step you opt into.

---

## The Three Inputs

### 1. Drop a file
Any file via the iCloud Junk Drawer folder or directly in chat.

**I do:**
1. Extract/describe what's in it
2. Save to `OneDrive/Hermy/Inbox/` with a clean filename
3. Say: *"📥 Got it — save, process (extract data), add to a task, or file somewhere?"*

### 2. Send a link
Any URL in the chat.

**I do:**
1. Fetch the page → summarise it in 2-3 bullets
2. Say: *"🔗 Here's the gist — save to Read Later, add context to a task, or ignore?"*

### 3. Type a half-thought
A fragment, a single word, a vibe.

**I do:**
- If it's obviously a command → execute it
- If it's ambiguous → ask one clarifying question (not three)
- If it's clearly a note fragment → save to `OneDrive/Hermy/Captures/` and say *"📝 Captured"*
- If you want to tell me to hold a thought without action → end with `→cap` and it's captured silently

---

## Setup: iCloud → Telegram File Drop (~2 min)

This sends any file you drop into an iCloud folder directly to me.

### Step 1: Create the iCloud folder
1. Open **Files** app
2. Tap **Browse** → **iCloud Drive**
3. Tap **•••** (three dots) → **New Folder**
4. Name it **`→ Junk Drawer`**

### Step 2: Build the Shortcut
1. Open **Shortcuts** app → **Automation** tab (bottom)
2. Tap **+** → **Create Personal Automation**
3. Scroll to **File** → **"When a new file appears in a folder"**
4. Tap **Choose Folder** → select **iCloud Drive / → Junk Drawer**
5. Tap **Next**
6. Tap **+ Add Action** → search for **"Send File"** → select **"Send File"**
7. Configure:
   - **File:** tap → **Shortcut Input**
   - **Recipient:** type **@jstew_hermes_bot** (your Herms bot)
   - **Message:** type `junk`
8. Toggle off **Ask Before Running**
9. Tap **Done**

### Step 3: Test it
Drop any file into your **`→ Junk Drawer`** iCloud folder. I'll see it here within seconds and let you know it landed.

## What Happens When a File Drops

| Moment | What I Do |
|---|---|
| File arrives | I see it in this chat — caption starts with "junk" |
| I download | Grab the file content from Telegram |
| I assess | Is it a contact export? A note? A photo? A document? |
| I save | Upload to `OneDrive/Hermy/Junk Drawer/` with datestamp prefix |
| I tell you | "📥 Landed in Junk Drawer: filename.ext (12KB)" |

## QC Gate (How I Decide)

| If it's... | I... |
|---|---|
| A document I recognize (export, note, list) | Save to Junk Drawer and file it in the right spot + tell you |
| A photo or image | Save to Junk Drawer + ask if it goes to Photos/ or Resources/ |
| Something I'm unsure about | Leave in Junk Drawer — tell you it's there and ask |
| Sensitive (PII, credentials) | Flag for your eyes only — won't process further without your OK |

Over time, I'll get enough reps to auto-file most things and only surface exceptions.

---

*Built by Herms for JStew — June 2026*
