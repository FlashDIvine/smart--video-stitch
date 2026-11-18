---
name: tiktok-uploader
description: Upload and publish videos automatically to TikTok Studio via Chrome/Brave browser CDP (port 9222). Use when the user requests posting, uploading, or publishing a video file to TikTok.
---

# TikTok Studio CDP Automated Publisher

## Overview
Automates uploading finished video files (MP4, MOV, WebM) directly to TikTok Studio (`https://www.tiktok.com/tiktokstudio/upload?from=upload`) using Chrome/Brave DevTools Protocol (CDP).

This bypasses manual web interactions and avoids fragile unofficial private APIs by driving the authenticated browser session directly.

---

## Prerequisites

1. **Browser Daemon with CDP Enabled:**
   Brave or Google Chrome running with remote debugging port `9222`:
   ```bash
   DISPLAY=:0 brave-browser --remote-debugging-port=9222 https://www.tiktok.com/tiktokstudio
   ```
2. **Authenticated Account:**
   The user must already be logged into TikTok in that browser profile.
3. **Node.js & Playwright:**
   `playwright-core` installed.

---

## Automated Publishing Workflow

```
[Connect to CDP :9222] ──> [Navigate to Upload Studio] ──> [Inject Video File]
          │
          ▼
[Purge Joyride Overlays] ──> [Write Caption & Tags] ──> [Click Posting]
          │
          ▼
[Handle Copyright Dialog] ──> [Wait for /content Redirect] ──> [Extract Live Video URL]
```

### Critical Edge Cases Handled

1. **Joyride Tour Interception (`#react-joyride-portal`):**
   TikTok Studio displays a multi-step tour modal that blocks pointer clicks on the caption editor. The script evaluates:
   ```javascript
   document.querySelectorAll('#react-joyride-portal, .react-joyride__overlay').forEach(el => el.remove());
   ```
2. **Unsaved Changes Dialog (`#tux-portal-container`):**
   If an accidental Escape or blur occurs, TikTok displays *"Anda yakin ingin keluar?"*. The script automatically clicks "Batal" (Cancel).
3. **Draft.js Rich Text Editor:**
   Caption is entered into `div.notranslate.public-DraftEditor-content` using keyboard text insertion to ensure hashtag suggestions don't break cursor focus.
4. **Copyright Check Confirmation:**
   When TikTok flags audio or presents *"Lanjut posting?"*, the script automatically clicks *"Posting sekarang"*.

---

## Standalone CLI Usage

The bundled CLI script is located at `scripts/tiktok_uploader.js`.

### 1. Basic Upload
```bash
node scripts/tiktok_uploader.js --file /path/to/video.mp4 --caption "My Epic AI Video! 🚀 #aivideo #fyp"
```

### 2. Upload with Caption from File
```bash
node scripts/tiktok_uploader.js --file /path/to/video.mp4 --caption-file /path/to/caption.txt
```

### 3. Pipeline JSON Output
```bash
node scripts/tiktok_uploader.js --file /path/to/video.mp4 --caption "Short title #viral" --json
```

---

## Verification & Output
The script automatically waits for navigation to `https://www.tiktok.com/tiktokstudio/content` and extracts the permalink of the newly created post (e.g. `https://www.tiktok.com/@username/video/7709482628306554120`). Always report this verified URL back to the user as proof of publication.
