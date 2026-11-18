#!/usr/bin/env python3
"""
Smart Video Stitcher Engine
An automated, lossless-first video concatenator using FFmpeg and FFprobe.
Handles audio synchronization (preventing Non-monotonic DTS warnings),
automatic compatibility checking, and post-processing verification.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def check_ffmpeg_installed() -> None:
    if not shutil.which("ffmpeg"):
        print("Error: 'ffmpeg' is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)
    if not shutil.which("ffprobe"):
        print("Error: 'ffprobe' is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)


def probe_file(file_path: Path) -> Dict[str, Any]:
    """Inspect video and audio properties using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {file_path}: {res.stderr}")

    data = json.loads(res.stdout)
    video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    format_info = data.get("format", {})

    fps = 0.0
    if video_stream and "r_frame_rate" in video_stream:
        r_fr = video_stream["r_frame_rate"]
        if "/" in r_fr:
            num, den = r_fr.split("/")
            fps = float(num) / float(den) if float(den) != 0 else 0.0
        else:
            fps = float(r_fr)

    return {
        "path": str(file_path),
        "duration": float(format_info.get("duration", 0.0)),
        "size_bytes": int(format_info.get("size", 0)),
        "has_video": video_stream is not None,
        "video_codec": video_stream.get("codec_name") if video_stream else None,
        "width": int(video_stream.get("width", 0)) if video_stream else 0,
        "height": int(video_stream.get("height", 0)) if video_stream else 0,
        "fps": fps,
        "has_audio": audio_stream is not None,
        "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
        "sample_rate": int(audio_stream.get("sample_rate", 0)) if audio_stream else 0,
        "channels": int(audio_stream.get("channels", 0)) if audio_stream else 0,
    }


def analyze_compatibility(probes: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Check if all video clips have identical stream properties for lossless stream copy."""
    if not probes:
        return False, "No video files provided"

    base = probes[0]
    for idx, p in enumerate(probes[1:], start=2):
        if p["width"] != base["width"] or p["height"] != base["height"]:
            return False, f"Resolution mismatch: File 1 ({base['width']}x{base['height']}) vs File {idx} ({p['width']}x{p['height']})"
        if p["video_codec"] != base["video_codec"]:
            return False, f"Codec mismatch: File 1 ({base['video_codec']}) vs File {idx} ({p['video_codec']})"
        if abs(p["fps"] - base["fps"]) > 0.05:
            return False, f"FPS mismatch: File 1 ({base['fps']:.2f}) vs File {idx} ({p['fps']:.2f})"

    return True, "All video streams are compatible for lossless concat"


def concat_demuxer(
    input_paths: List[Path],
    output_path: Path,
    reencode_audio: bool = True,
    audio_bitrate: str = "192k",
    overwrite: bool = True,
) -> None:
    """Concatenate files using ffmpeg concat demuxer."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        temp_list_path = f.name
        for p in input_paths:
            # Escape single quotes in filenames for ffmpeg manifest
            escaped_path = str(p.resolve()).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    try:
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", temp_list_path,
            "-c:v", "copy",
        ]

        if reencode_audio:
            # Audio re-encode avoids Non-monotonic DTS warnings and timestamp jitter
            cmd.extend(["-c:a", "aac", "-b:a", audio_bitrate])
        else:
            cmd.extend(["-c:a", "copy"])

        if overwrite:
            cmd.append("-y")

        cmd.append(str(output_path))

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg concat failed:\n{res.stderr}")
    finally:
        if os.path.exists(temp_list_path):
            os.remove(temp_list_path)


def concat_filter_complex(
    input_paths: List[Path],
    output_path: Path,
    target_width: int,
    target_height: int,
    audio_bitrate: str = "192k",
    overwrite: bool = True,
) -> None:
    """Fallback re-encoding concat using filter_complex for clips with differing dimensions."""
    cmd = ["ffmpeg"]
    for p in input_paths:
        cmd.extend(["-i", str(p)])

    filter_parts = []
    n = len(input_paths)
    for i in range(n):
        # Scale and pad to fit target dimension while preserving aspect ratio
        filter_parts.append(
            f"[{i}:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
            f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}];"
        )

    concat_inputs = "".join([f"[v{i}][{i}:a]" for i in range(n)])
    filter_parts.append(f"{concat_inputs}concat=n={n}:v=1:a=1[outv][outa]")

    cmd.extend([
        "-filter_complex", "".join(filter_parts),
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", audio_bitrate,
    ])

    if overwrite:
        cmd.append("-y")

    cmd.append(str(output_path))

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg filter_complex concat failed:\n{res.stderr}")


def stitch(
    input_files: List[Path],
    output_file: Path,
    mode: str = "auto",
    reencode_audio: bool = True,
    audio_bitrate: str = "192k",
    overwrite: bool = True,
) -> Dict[str, Any]:
    """Main orchestration function to probe, analyze, merge, and verify."""
    check_ffmpeg_installed()

    if len(input_files) < 2:
        raise ValueError("At least two input video files are required to stitch.")

    # 1. Probing
    probes = [probe_file(p) for p in input_files]
    compatible, reason = analyze_compatibility(probes)
    expected_duration = sum(p["duration"] for p in probes)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 2. Execution
    actual_strategy = "demuxer"
    if mode == "reencode" or (mode == "auto" and not compatible):
        actual_strategy = "filter_complex"
        target_w = probes[0]["width"] or 1080
        target_h = probes[0]["height"] or 1920
        concat_filter_complex(
            input_paths=input_files,
            output_path=output_file,
            target_width=target_w,
            target_height=target_h,
            audio_bitrate=audio_bitrate,
            overwrite=overwrite,
        )
    else:
        concat_demuxer(
            input_paths=input_files,
            output_path=output_file,
            reencode_audio=reencode_audio,
            audio_bitrate=audio_bitrate,
            overwrite=overwrite,
        )

    # 3. Post-verification
    if not output_file.exists():
        raise FileNotFoundError(f"Output file {output_file} was not generated.")

    out_probe = probe_file(output_file)

    return {
        "status": "success",
        "strategy": actual_strategy,
        "compatibility_reason": reason,
        "input_count": len(input_files),
        "expected_duration": expected_duration,
        "output_duration": out_probe["duration"],
        "output_file": str(output_file.resolve()),
        "output_size_mb": round(out_probe["size_bytes"] / (1024 * 1024), 2),
        "resolution": f"{out_probe['width']}x{out_probe['height']}",
        "video_codec": out_probe["video_codec"],
        "audio_codec": out_probe["audio_codec"],
    }


def find_video_files(directory: Path) -> List[Path]:
    """Find and sort video files in a directory."""
    extensions = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
    files = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in extensions]
    return sorted(files, key=lambda f: f.name)


def main():
    parser = argparse.ArgumentParser(
        description="Smart Video Stitcher: Combine video clips safely, seamlessly, and losslessly."
    )
    parser.add_argument("inputs", nargs="*", help="List of video files in stitching order.")
    parser.add_argument("--dir", "-d", type=str, help="Directory containing video clips to merge.")
    parser.add_argument("--output", "-o", type=str, required=True, help="Destination output file path.")
    parser.add_argument(
        "--mode", "-m", choices=["auto", "lossless", "reencode"], default="auto",
        help="Concat mode: 'auto' (default: lossless if compatible, else re-encode), 'lossless', 'reencode'."
    )
    parser.add_argument(
        "--copy-audio", action="store_true",
        help="Copy audio stream without re-encoding (caution: may cause DTS timestamp warnings)."
    )
    parser.add_argument("--audio-bitrate", default="192k", help="Audio bitrate when re-encoding (default: 192k).")
    parser.add_argument("--json", action="store_true", help="Print summary in JSON format.")

    args = parser.parse_args()

    input_paths: List[Path] = []
    if args.dir:
        input_paths = find_video_files(Path(args.dir))
    elif args.inputs:
        input_paths = [Path(p) for p in args.inputs]

    if not input_paths:
        print("Error: No input video files provided. Specify files or use --dir.", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output)
    reencode_audio = not args.copy_audio

    try:
        report = stitch(
            input_files=input_paths,
            output_file=out_path,
            mode=args.mode,
            reencode_audio=reencode_audio,
            audio_bitrate=args.audio_bitrate,
        )

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("\n Stitching Complete!")
            print(f"Output File     : {report['output_file']}")
            print(f"Strategy        : {report['strategy']}")
            print(f"Total Clips     : {report['input_count']}")
            print(f"Total Duration  : {report['output_duration']:.2f}s (Expected: {report['expected_duration']:.2f}s)")
            print(f"Resolution      : {report['resolution']}")
            print(f"File Size       : {report['output_size_mb']} MB")
            print(f"Video / Audio   : {report['video_codec']} / {report['audio_codec']}")

    except Exception as e:
        print(f"\n Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
