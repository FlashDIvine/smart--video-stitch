# Video Processing & Media Rules for AI Agents

When working with video and multimedia files in this project:

## 1. Safety & File Integrity
* **Never Overwrite Raw Sources:** Never modify or overwrite source clips (`input` or raw recordings) unless explicitly asked by the user.
* **Distinct Output Naming:** Always write to a dedicated output file (e.g. `gabungan.mp4`, `output.mp4`, or `{folder}_merged.mp4`).

## 2. Mandatory Pre-Flight Inspection (Probe Before Stitch)
* **Inspect Every Input:** Always probe all input videos with `ffprobe` prior to merging:
  - Check video resolution (`width` x `height`) and aspect ratio (e.g. 9:16 vs 16:9).
  - Check frame rate (`r_frame_rate`).
  - Check video codec (`h264`, `hevc`, `vp9`, etc.).
  - Check audio stream presence, codec (`aac`, `opus`, etc.), sample rate, and channels.
* **Determine Concat Strategy:**
  - If resolutions, codecs, and frame rates match: Prefer Concat Demuxer with lossless video stream copy (`-c:v copy`).
  - For audio: Re-encode audio to AAC (`-c:a aac -b:a 192k`) rather than raw audio stream copy to prevent timestamp jitter and `Non-monotonic DTS` errors between segmented clips.
  - If resolutions differ: Re-encode video using scale/pad filter to maintain consistent dimensions (e.g. 1080x1920) without distorting aspect ratios.

## 3. Evidence Before Claims (Verification)
* **Never Declare Done Blindly:** Do not report success until running `ffprobe` on the final output file.
* **Verify Key Metrics:** Check and report:
  - Output duration vs total expected sum of inputs.
  - Video stream existence and valid frame count.
  - Audio stream existence and synchronization.
  - Final file size in MB.

## 4. Sanitation
* **Clean Manifests:** Always delete temporary manifest files (such as `list.txt` or temporary cut lists) immediately after FFmpeg completes.
