# ☁️ iCloud → OneDrive Intake Framework

## The Pipeline

```
Your iCloud / "→ Herms Inbox" Folder
        ↓
Shortcut Automation (triggered when file added)
        ↓
OneDrive/Hermy/Inbox/   ← RAW QUARANTINE
        ↓
Herms reviews daily     ← QC GATE
        ↓
OneDrive/Hermy/Organized/  or  OneDrive/Hermy/Trash/
```

## The Folders

| Folder | Purpose | Who moves files here |
|---|---|---|
| **iCloud / "→ Herms Inbox"** | Your drop zone — put any file here to send to me | You (via Files app or Share Sheet) |
| **OneDrive/Hermy/Inbox/** | Raw quarantine — I review everything here before it goes anywhere | Shortcut Automation |
| **OneDrive/Hermy/Organized/** | Where I put files after review — sorted by context | Herms |
| **OneDrive/Hermy/Trash/** | What I'd discard, held 7 days before auto-delete | Herms (with your confirmation) |

## The Intake Rules (QC Gate)

When I see a file in Inbox, I ask:

1. **Is it yours?** — A document you created or a file you intentionally saved?
2. **Does it belong in our workspace?** — Relevant to our projects, CRM, notes, or archive?
3. **Is it sensitive?** — PII, credentials, personal photos? Those go to `_system/` or get flagged for your review.
4. **Is it a duplicate?** — Already exists somewhere?

**Outcomes:**

| Check | Result |
|---|---|
| ✅ Clear — belongs in workspace | → Organized/ with note to you |
| ⚠️ Unsure | → Leave in Inbox, ask you |
| ❌ Not ours | → Trash/ (held 7 days) |
| 🔒 Sensitive | → Flag for your review |

## How to Use (Build the Shortcut)

### Step 1: Create the iCloud Folder
On your iPhone/iPad:
1. Open **Files** app
2. Tap **Browse** → **iCloud Drive**
3. Tap **•••** (three dots) → **New Folder**
4. Name it **`→ Herms Inbox`**

### Step 2: Build the Shortcut
1. Open **Shortcuts** app → **Automation** tab (bottom)
2. Tap **+** → **Create Personal Automation**
3. Scroll to **File** → select **"Files"** → **"When a new file appears in a folder"**
4. Tap **Choose Folder** → select **iCloud Drive / → Herms Inbox**
5. Tap **Next**
6. Tap **+ Add Action** → search for **"Get Contents of URL"**
7. Configure:
   - **URL:** `https://api.onedrive.com/v1.0/drive/special/approot:/Inbox/{{File Name}}:/content?@name.conflictBehavior=replace`
   - **Method:** **PUT**
   - **Headers:** Add header `Authorization` = `Bearer YOUR_TOKEN_HERE`
   - **Request Body:** **File** → select **Shortcut Input**
8. Tap **Next**
9. Toggle off **Ask Before Running**
10. Tap **Done**

### Step 3: Get Your OneDrive Token
I'll get this for you — it's the same Graph token the workspace uses. I'll set it up so the Shortcut can use it securely.

→ **I'll handle the token plumbing.** For now, just create the iCloud folder and the Shortcut skeleton.

## My Daily Review

Every morning, I scan Inbox and report:

> **📥 Inbox: 2 new files**
> - `Q3_Strategy.pdf` → Moved to Organized/Hunting
> - `photo_001.jpg` → Unsure — does this belong here?
> - Trash is empty ✓

## Safety Guarantees

- **I never auto-file to your real OneDrive structure** without review
- **I never delete** without your confirmation
- **Sensitive files** are flagged, not processed
- **You can always check Trash** before it's cleared

---

*Built by Herms for JStew — June 2026*
