---
name: smart-video-stitch
description: Use when concatenating, merging, or stitching multiple video files, especially for Shorts, Reels, TikTok, or general video assembly where audio synchronization and lossless quality are critical.
---

# Smart Video Stitch

## Overview
Concatenating video clips with raw FFmpeg is prone to subtle bugs:
- **Audio Desync & Non-monotonic DTS:** Occurs when using `-c:a copy` across fragmented MP4 files with micro-offset audio timestamps.
- **Resolution/Aspect Ratio Distortions:** Occurs when concatenating clips with differing dimensions or SAR (Sample Aspect Ratio).
- **Silent Failures:** Occurs when FFmpeg exits with partial files or mismatched durations.

This skill provides a battle-tested, 4-phase pipeline to inspect, decide, stitch, and verify video files.

---

## The 4-Phase Pipeline

```
[Phase 1: Probing] ──> [Phase 2: Decision Tree] ──> [Phase 3: Execution] ──> [Phase 4: Verification]
```

### Phase 1: Probing & Pre-Flight Check
Always probe every input file before running any concatenation:

```bash
ffprobe -v error -show_entries stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels -show_entries format=duration,size -of default=noprint_wrappers=1 "input.mp4"
```

Verify:
1. Video resolution (`width` x `height`)
2. Video frame rate (`r_frame_rate`)
3. Video codec (`codec_name`)
4. Audio presence and sample rate (`sample_rate`)
5. Total expected duration (sum of individual durations)

### Phase 2: Decision Tree

```
Are all video dimensions, codecs, and frame rates identical?
 ├── YES ──> Strategy A: Concat Demuxer (Lossless Video Copy)
 │           - Video: Stream Copy (`-c:v copy`) -> 100% original quality, zero re-encode time
 │           - Audio: Re-encode AAC (`-c:a aac -b:a 192k`) -> Guarantees seamless timestamp alignment
 │
 └── NO  ──> Strategy B: Filter Complex Concat (Uniform Harmonization)
             - Scale and pad to target resolution (e.g., 1080x1920 for 9:16 Shorts)
             - Unified framerate and audio sample rate
```

> [!IMPORTANT]
> **Why not `-c copy` for both?**
> When merging independent MP4 clips, raw `-c copy` often produces `Non-monotonic DTS; previous: X, current: Y` warnings. This causes audio pops, audio-video desync, or playback stutter in media players and social media uploaders. Re-encoding only the audio stream (`-c:a aac -b:a 192k`) takes milliseconds and eliminates all timestamp jitter.

### Phase 3: Execution

#### Strategy A: Concat Demuxer (Fast & Lossless)
1. Generate temporary manifest (`list.txt`):
   ```text
   file '/absolute/path/to/01.mp4'
   file '/absolute/path/to/02.mp4'
   file '/absolute/path/to/03.mp4'
   ```
2. Execute FFmpeg:
   ```bash
   ffmpeg -f concat -safe 0 -i list.txt -c:v copy -c:a aac -b:a 192k output.mp4 -y
   ```
3. Remove temporary manifest immediately:
   ```bash
   rm -f list.txt
   ```

#### Strategy B: Filter Complex (Different Dimensions / Codecs)
```bash
ffmpeg -i input1.mp4 -i input2.mp4 \
  -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[v0]; \
                   [1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[v1]; \
                   [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" -c:v libx264 -preset fast -crf 20 -c:a aac -b:a 192k output.mp4 -y
```

### Phase 4: Verification (Evidence Before Claims)
Before reporting completion to the user, run:

```bash
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 "output.mp4"
```

Confirm:
- Output duration matches expected sum (within a few milliseconds).
- Video and audio streams are both present and intact.
- File size is non-zero and reasonable.

---

## Bundled Helper Script

This skill bundles an automated Python engine located at `scripts/stitcher.py`. You can invoke it directly:

```bash
# Merge clips in a directory automatically:
python3 <skill-dir>/scripts/stitcher.py --dir /path/to/clips -o /path/to/output.mp4

# Merge specific files in order:
python3 <skill-dir>/scripts/stitcher.py clip1.mp4 clip2.mp4 clip3.mp4 -o final.mp4

# Output JSON report for automated pipelines:
python3 <skill-dir>/scripts/stitcher.py --dir /path/to/clips -o final.mp4 --json
```
