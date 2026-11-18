# 🎬 Smart Video Stitch

**A lossless-first video concatenator, AI video prompt engineering framework, and automated TikTok Studio publisher for Antigravity & AI Agents.**

Easily merge fragmented video clips (such as YouTube Shorts, Instagram Reels, TikTok, or multi-part AI recordings) with zero quality loss, rock-solid audio synchronization, automated quality verification, and one-click direct publishing to TikTok Studio.

---

## 💡 Key Features & The Problems This Solves

### 1. Lossless & Glitch-Free Video Concatenation
* **Audio Desync & DTS Timestamp Glitches:** Naively running `ffmpeg -c copy` on separated MP4 clips triggers `Non-monotonic DTS` warnings, creating audio pops and playback stutter. **Smart Video Stitch** copies video streams losslessly (`-c:v copy`) while re-encoding audio to AAC (`-c:a aac -b:a 192k`), ensuring zero video quality degradation with microsecond-accurate audio sync.
* **Resolution Harmonization:** Automatically scales and letterboxes/pillarboxes clips if resolutions differ.

### 2. Dialogue & Speech Preservation (Anti-Cutoff Invariant)
* Tail trimming (`--clip-duration 7.4` or `--trim-tail 0.6`) removes generative AI tail-freeze glitches on silent slapstick clips.
* **Invariant:** Clips with spoken voiceover or dialogue are automatically preserved **uncut** (e.g. full 8s × 3 = 24s) to ensure trailing words and syllables are never severed.

### 3. Production AI Video Prompt SOP Framework (`rules/PROMPT_RULES.md`)
* Complete 8-pillar prompt engineering architecture designed for Google Veo 3.1 & Flow.
* Eliminates phantom floating text, anatomy morphing, and wild 360° camera spinning.
* Strict physical screen bounding rules: text and UI elements are strictly contained within in-world computer monitors, tablets, or holographic boards.

### 4. Direct TikTok Studio Publishing via CDP (`scripts/tiktok_uploader.js`)
* Fully automated video publishing to TikTok Studio (`https://www.tiktok.com/tiktokstudio/upload`).
* Automatically connects to your running Chrome/Brave browser via CDP (port 9222).
* Automatically bypasses Joyride tour popups (`#react-joyride-portal`), unsaved changes modals (`#tux-portal-container`), and copyright check prompts.
* Writes rich captions & hashtags, clicks publish, and returns the verified live post link.

---

## 📂 Repository Structure

```text
smart-video-stitch/
├── plugin.json                 # Antigravity Plugin manifest
├── README.md                   # Documentation & quickstart
├── LICENSE                     # MIT License
├── rules/
│   ├── AGENTS.md               # Safety, speech preservation & publishing rules for AI agents
│   └── PROMPT_RULES.md         # 8-Pillar SOP Prompt Engineering framework for Veo 3.1 / Flow
├── scripts/
│   └── tiktok_uploader.js      # Automated TikTok Studio CDP publishing CLI
└── skills/
    ├── smart-video-stitch/
    │   ├── SKILL.md            # Concatenation SOP guide for AI agents
    │   └── scripts/
    │       └── stitcher.py     # Standalone Python FFmpeg concatenation engine
    └── tiktok-uploader/
        └── SKILL.md            # TikTok Studio CDP publishing skill for AI agents
```

---

## 🚀 Installation

### Option 1: Global Antigravity Plugin (Recommended)
Clone directly into your global Antigravity plugins directory:

```bash
git clone https://github.com/FlashDIvine/smart--video-stitch.git ~/.gemini/config/plugins/smart-video-stitch
```

### Option 2: Project-Level Plugin
Clone directly into your project's `.agents/plugins/` directory:

```bash
git clone https://github.com/FlashDIvine/smart--video-stitch.git .agents/plugins/smart-video-stitch
```

---

## 💬 Usage with Antigravity / AI Agent

### Stitching Videos
Simply prompt your agent naturally:
```text
"Tolong gabungkan semua video di folder ./clips menjadi satu video Shorts tanpa memotong dialog suara"
```
The agent inspects all clips with `ffprobe`, selects the optimal stream-copy strategy, and runs verification before reporting success.

### Publishing to TikTok
```text
"Post video final.mp4 ke TikTok dengan caption 'Tutorial AI Video Otomatis 🚀 #aivideo #fyp'"
```
The agent invokes the `tiktok-uploader` skill, connects to your logged-in browser session, injects the video and caption, confirms publishing, and returns the live video URL.

---

## 💻 Standalone CLI Usage (Terminal / Scripts)

### 1. Stitching Videos
```bash
# Merge clips in a directory losslessly:
python3 skills/smart-video-stitch/scripts/stitcher.py --dir /path/to/clips -o /path/to/output.mp4

# Merge clips while trimming tail-freeze artifacts (silent clips only):
python3 skills/smart-video-stitch/scripts/stitcher.py --dir /path/to/clips -o final.mp4 --clip-duration 7.4

# Merge specific files in order:
python3 skills/smart-video-stitch/scripts/stitcher.py clip1.mp4 clip2.mp4 clip3.mp4 -o final.mp4

# Output JSON report:
python3 skills/smart-video-stitch/scripts/stitcher.py --dir /path/to/clips -o final.mp4 --json
```

### 2. Publishing to TikTok Studio
Start Chrome or Brave with remote debugging enabled:
```bash
brave-browser --remote-debugging-port=9222 https://www.tiktok.com/tiktokstudio
```

Then run the publisher:
```bash
# Publish with direct caption:
node scripts/tiktok_uploader.js --file ./final.mp4 --caption "My Epic AI Video! 🎬 #fyp #aivideo"

# Publish with caption loaded from file:
node scripts/tiktok_uploader.js --file ./final.mp4 --caption-file ./caption.txt

# Output JSON format:
node scripts/tiktok_uploader.js --file ./final.mp4 --caption "Short title #viral" --json
```

---

## 📋 Requirements
* Python 3.8+
* `ffmpeg` and `ffprobe` installed on your system (`sudo apt install ffmpeg`).
* Node.js 18+ and `playwright-core` (for TikTok automated publishing).

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
