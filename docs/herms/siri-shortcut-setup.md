# Siri-to-Hermes Shortcut Setup Guide

## What This Does

Trigger: "Hey Siri, tell Herms [thought/idea/task/question]"
Flow: Record audio → Send to Telegram Bot API → Gateway transcribes → Hermes responds → You check Telegram later

## Step-by-Step

### On Your iPhone

1. **Open the Shortcuts app**
2. Tap **+** (top right) → **Add Action**

### Step 1 — Recording
3. Search for **"Record Audio"** and add it
4. Leave it as default (no duration limit, show while recording)

### Step 2 — Set Variable
5. Tap the **Record Audio** block
6. Tap **"Recording"** → **Set Variable** → name it `AudioFile`

### Step 3 — Base64 Encode (for reliable audio sending)
7. Search for **"Base64 Encode"** and add it
8. Set input to the `AudioFile` variable

### Step 4 — Send to Telegram
9. Search for **"Get Contents of URL"** and add it
10. Configure:

| Field | Value |
|---|---|
| **URL** | `https://api.telegram.org/bot8974639633:AAHqgAVcM9IhRlbNnmLystK7cNrvAc5lKIs/sendAudio` |
| **Method** | `POST` |
| **Headers** | Leave empty |
| **Request Body** | `Form` |
| Add field: `chat_id` = `8327493830` |
| Add field: `audio` = `File` → select `AudioFile` variable |
| Add field: `caption` = `📱 Siri` (or whatever note you want) |

⚠️ **Important:** Shortcuts sometimes strips the audio file type. If the above doesn't work perfectly, swap `sendAudio` for `sendDocument` — it's more forgiving with file formats:
- URL: `https://api.telegram.org/bot8974639633:AAHqgAVcM9IhRlbNnmLystK7cNrvAc5lKIs/sendDocument`
- Add field: `document` = `File` → `AudioFile`
- Same `chat_id` and `caption`

### Step 5 — Confirm
11. Search for **"Show Notification"** and add it
12. Title: `Sent to Herms ✅`
13. Body: Leave blank or add `{{AudioFile Name}}`

### Step 6 — Done
14. Tap **Next** (top right)
15. Name: **"Tell Herms"**
16. Tap **Done**

### Step 7 — Add to Siri
17. In your shortcut list, tap **"Tell Herms"**
18. Tap the **•••** (three dots)
19. Tap the **shortcut name** at the top → **Add to Siri**
20. Record the phrase: **"Hey Siri, tell Herms"**

## Usage

| Trigger | Result |
|---|---|
| "Hey Siri, tell Herms" | Starts recording. Tap to stop. Sends to me. You get a notification. |
| → I process, transcribe, and reply | Check Telegram whenever free. |
| Can also run from Lock Screen (Siri widget) or Back Tap | No app opening needed. |

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Not Found" from Telegram | Token might have been truncated. Re-check the bot token in BotFather |
| Audio doesn't arrive | Try `sendDocument` instead of `sendAudio` in the URL |
| File too large | Telegram limit is 50MB for audio. Short recordings are fine |
| Caption has gibberish | Leave caption empty — it's optional |

## Testing

To test before Siri:
1. Open Shortcuts app
2. Tap **"Tell Herms"**
3. Tap **▶️** (play button at bottom)
4. Record a quick "testing" and tap stop
5. Wait for notification
6. Check Telegram for my response
