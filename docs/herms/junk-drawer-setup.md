# 🗂️ Junk Drawer — iCloud → Herms File Pipeline

## The Pipeline

```
You save a file to "→ Junk Drawer" in iCloud
        ↓ (Shortcut Automation — auto-sends to Telegram)
Bot sends it as a document with caption "junk"
        ↓ (Gateway receives, I see it)
I download, assess, and save to OneDrive/Hermy/Junk Drawer/
        ↓ (I notify you what I did)
You see "📥 Landed in Junk Drawer" with my assessment
```

## What You Do on iPhone (~2 min)

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
