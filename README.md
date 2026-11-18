# 🎬 Smart Video Stitch

**A lossless-first, automated video concatenation plugin for Antigravity & AI Agents.**

Easily merge fragmented video clips (such as YouTube Shorts, Instagram Reels, TikTok, or multi-part recordings) with zero quality loss, rock-solid audio synchronization, and automated quality verification.

---

## 💡 The Problem This Solves

Merging video clips using raw FFmpeg often introduces subtle, frustrating bugs:
* **Audio Desync & Stutter:** Naively running `ffmpeg -c copy` on separated MP4 clips often triggers `Non-monotonic DTS` warnings, creating audio pops or desynchronization in video players and social media uploaders.
* **Resolution Mismatch:** Stitching clips with differing resolutions or sample aspect ratios causes stretched or distorted videos.
* **Silent Failures:** Partial files or truncated durations when an error occurs silently.

**Smart Video Stitch** solves this by implementing a **4-Phase Smart Pipeline**:
1. **Pre-flight Probing:** Automatically checks video dimensions, framerates, codecs, and audio sample rates using `ffprobe`.
2. **Lossless-First Decision Matrix:** Uses FFmpeg Concat Demuxer with video stream copy (`-c:v copy`) for instant, 100% original quality, while automatically re-encoding audio (`-c:a aac -b:a 192k`) to guarantee seamless timestamp synchronization without DTS errors.
3. **Smart Fallback:** Seamlessly scales and pads clips (letterbox/pillarbox) if aspect ratios differ.
4. **Post-Processing QA:** Verifies the final file duration and stream integrity before declaring success.

---

## 📂 Repository Structure

```text
smart-video-stitch/
├── plugin.json                 # Antigravity Plugin manifest
├── README.md                   # Documentation & quickstart
├── LICENSE                     # MIT License
├── rules/
│   └── AGENTS.md               # Quality and safety rules enforced on AI agents
└── skills/
    └── smart-video-stitch/
        ├── SKILL.md            # SOP guide for AI agents
        └── scripts/
            └── stitcher.py     # Standalone Python CLI & engine
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

Once installed, simply prompt your agent naturally:

```text
"Tolong gabungkan semua video di folder /home/najib/Dokumen/Yutub/cat1 menjadi satu file"
```
or in English:
```text
"Merge all the video clips inside ./footage into a single vertical short video"
```

The agent will automatically invoke the `smart-video-stitch` skill, inspect the clips, choose the optimal strategy, run the concatenation, and verify the output.

---

## 💻 Standalone CLI Usage (Without AI)

You can also use the bundled Python script directly in your terminal:

```bash
# Merge all video files in a directory:
python3 skills/smart-video-stitch/scripts/stitcher.py --dir /path/to/clips -o /path/to/output.mp4

# Merge specific files in order:
python3 skills/smart-video-stitch/scripts/stitcher.py clip1.mp4 clip2.mp4 clip3.mp4 -o final.mp4

# Output JSON report (useful for scripts & CI/CD):
python3 skills/smart-video-stitch/scripts/stitcher.py --dir /path/to/clips -o final.mp4 --json
```

---

## 📋 Requirements
* Python 3.8+
* `ffmpeg` and `ffprobe` installed on your system (e.g. `sudo apt install ffmpeg` on Debian/Ubuntu).

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
