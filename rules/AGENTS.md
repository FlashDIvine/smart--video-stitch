# Video Processing, AI Generation & Publishing Rules for AI Agents

When working with video production, prompt generation, stitching, and publishing in this project:

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

## 5. Dialogue & Speech Preservation (Anti-Cutoff Invariant)
* **Never Blindly Trim Clips with Dialogue:** Jika klip video berisi dialog vokal, monolog, atau voiceover, **DILARANG KERAS** memotong durasi klip (seperti `--clip-duration 7.4` atau `--trim-tail 0.6`). Seluruh klip wajib digabungkan secara utuh (*uncut*, misal 8s × 3 = 24.12s) agar kata atau suku kata terakhir tidak terpenggal.
* **Conditional Trimming Only:** Pemotongan ekor (`--trim-tail` / `--clip-duration`) hanya boleh diterapkan jika klip diverifikasi 100% bisu (*silent slapstick* tanpa dialog suara) untuk membuang artefak statis, atau atas instruksi eksplisit pengguna.

## 6. AI Video Prompt Engineering Standard
* **Mandatory SOP Structure:** Saat menyusun prompt untuk model generasi video AI (seperti Google Veo 3.1 & Flow), agen **WAJIB** mengikuti format 8-Pilar baku pada `rules/PROMPT_RULES.md`:
  1. `SHOT AWAL`: Framing, entity referensi, dan batas fisik prop/layar.
  2. `GERAKAN KAMERA`: Timeline kamera per detik (locked-off atau slow push-in; dilarang putaran liar).
  3. `AKSI KARAKTER & TAMPILAN MONITOR`: Aksi kronologis tunggal per rentang waktu.
  4. `DIALOG`: Teks dialog vokal kata-per-kata + emosi dan panduan gerak bibir.
  5. `LARANGAN MUTLAK`: Zero morphing, larangan teks melayang di luar layar fisik, jari tepat 5.
  6. `GAYA VISUAL`: Shader 3D / claymation, pencahayaan rim-light, Octane render, foley sound.
  7. `FINAL VISUAL PRIORITY`: Urutan prioritas difusi (Identitas > Logika/Teks > Batas Layar > Kontinuitas > Aksi > Efek).
* **Physical Screen Constraint:** Seluruh teks, angka, simbol matematika, atau grafik informasi **HANYA** boleh tampil di dalam batas monitor komputer, tablet fisik, atau papan hologram. **Dilarang keras membiarkan teks melayang bebas di udara.**

## 7. Automated Social Media Publishing Safety (TikTok Studio CDP)
* **Pre-Flight Port Check:** Pastikan browser Chrome/Brave telah berjalan dengan opsi `--remote-debugging-port=9222` sebelum memulai otomasi.
* **Remove Blocking Overlays:** Selalu bersihkan `#react-joyride-portal` dan `.react-joyride__overlay` dari DOM untuk mencegah *pointer event interception*.
* **Handle Dialogs Safely:**
  - Tangani modal konfirmasi keluar (`#tux-portal-container`) dengan menekan batal/tetap di halaman jika terpanggil.
  - Tangani modal *Copyright Check* dengan menekan konfirmasi *"Posting sekarang"*.
* **Verify Live URL Before Completion:** Jangan klaim proses posting selesai sebelum memverifikasi pengalihan URL ke `https://www.tiktok.com/tiktokstudio/content` dan mengekstrak tautan publik video (`/@username/video/...`).
