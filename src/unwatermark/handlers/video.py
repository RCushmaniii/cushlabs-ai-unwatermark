"""Video file handler — removes NotebookLM watermark from videos.

Uses a "clean patch" approach: process ONE reference frame through the
watermark removal pipeline, extract the cleaned region as a patch, then
use FFmpeg to overlay that patch onto every frame. This costs exactly one
LaMa API call regardless of video length and preserves audio.
"""

from __future__ import annotations

import gc
import json
import logging
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.multipass import clean_image
from unwatermark.models.annotation import UserAnnotation

logger = logging.getLogger(__name__)

MAX_DURATION_SECONDS = 300  # 5 minutes
SUPPORTED_EXTENSIONS = {".mp4", ".webm", ".mov"}


def process_video(
    input_path: Path,
    output_path: Path,
    config: Config,
    annotation: UserAnnotation | None = None,
    force_strategy: str | None = None,
    on_progress: Callable[[str, int], None] | None = None,
) -> Path:
    """Remove watermark from a video file.

    Extracts a reference frame, removes the watermark from it, then uses
    FFmpeg to composite the clean patch onto every frame of the video.

    Args:
        input_path: Path to the source video.
        output_path: Path to write the cleaned video.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.
        on_progress: Callback(message, percent) for progress updates.

    Returns:
        Path to the output file.
    """

    def _emit(msg: str, pct: int) -> None:
        if on_progress:
            on_progress(msg, pct)

    _check_ffmpeg()

    # Probe video metadata
    _emit("Analyzing video...", 5)
    info = _probe_video(input_path)
    duration = info["duration"]
    width = info["width"]
    height = info["height"]
    has_audio = info["has_audio"]

    if duration > MAX_DURATION_SECONDS:
        raise ValueError(
            f"Video is {duration:.0f}s — maximum is {MAX_DURATION_SECONDS}s (5 minutes)"
        )

    logger.warning(
        f"Video: {width}x{height}, {duration:.1f}s, audio={'yes' if has_audio else 'no'}"
    )

    with tempfile.TemporaryDirectory(prefix="unwatermark_video_") as tmp_dir:
        tmp = Path(tmp_dir)

        # Extract a reference frame at ~1s (avoids title cards)
        _emit("Extracting reference frame...", 10)
        seek_time = min(1.0, duration / 2)
        ref_frame_path = tmp / "ref_frame.png"
        _extract_frame(input_path, ref_frame_path, seek_time)

        # Run the watermark removal pipeline on the reference frame
        _emit("Detecting watermark...", 15)
        ref_image = Image.open(ref_frame_path)

        def sub_progress(msg: str, pct: int) -> None:
            # Map clean_image progress (10-95) into our 15-50 range
            scaled = 15 + int((pct / 100) * 35)
            _emit(msg, min(scaled, 50))

        result = clean_image(
            ref_image, config, annotation, force_strategy,
            on_progress=sub_progress,
        )
        gc.collect()

        if result.removed == 0:
            _emit("No watermark found — copying original video", 95)
            import shutil
            shutil.copy2(input_path, output_path)
            _emit("Done — no watermark detected", 100)
            return output_path

        # Determine the watermark region from the detection result
        if result.first_analysis is None:
            # Fallback: use the fixed NotebookLM bottom-right region
            region_x = int(width * 0.88)
            region_y = int(height * 0.94)
            region_w = width - region_x
            region_h = height - region_y
        else:
            r = result.first_analysis.region
            region_x = r.x
            region_y = r.y
            region_w = r.width
            region_h = r.height

        # Extract the clean patch from the inpainted frame
        _emit("Preparing clean patch...", 55)
        patch = result.image.crop((
            region_x, region_y,
            region_x + region_w, region_y + region_h,
        ))
        patch_path = tmp / "patch.png"
        patch.save(patch_path, format="PNG")

        logger.warning(
            f"Clean patch: ({region_x},{region_y}) {region_w}x{region_h}"
        )

        # Free PIL images before FFmpeg
        del ref_image, result, patch
        gc.collect()

        # Composite the patch onto every frame with FFmpeg
        _emit("Processing video...", 60)
        _composite_video(
            input_path=input_path,
            patch_path=patch_path,
            overlay_x=region_x,
            overlay_y=region_y,
            output_path=output_path,
            has_audio=has_audio,
            duration=duration,
            on_progress=lambda msg, pct: _emit(msg, 60 + int(pct * 0.35)),
        )

    _emit("Done — watermark removed from video", 100)
    return output_path


def _check_ffmpeg() -> None:
    """Verify FFmpeg is installed."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, timeout=10,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "FFmpeg is not installed. Video processing requires FFmpeg."
        )


def _probe_video(path: Path) -> dict:
    """Get video metadata using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            str(path),
        ],
        capture_output=True, text=True, timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)

    # Find video stream
    video_stream = None
    has_audio = False
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and video_stream is None:
            video_stream = stream
        if stream.get("codec_type") == "audio":
            has_audio = True

    if video_stream is None:
        raise ValueError("No video stream found in file")

    duration = float(data.get("format", {}).get("duration", 0))
    if duration == 0:
        # Try stream-level duration
        duration = float(video_stream.get("duration", 0))

    return {
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
        "duration": duration,
        "has_audio": has_audio,
    }


def _extract_frame(video_path: Path, output_path: Path, seek_time: float) -> None:
    """Extract a single frame from the video."""
    result = subprocess.run(
        [
            "ffmpeg",
            "-ss", str(seek_time),
            "-i", str(video_path),
            "-frames:v", "1",
            "-q:v", "2",
            str(output_path),
            "-y",
        ],
        capture_output=True, timeout=30,
    )

    if result.returncode != 0 or not output_path.exists():
        raise RuntimeError(f"Failed to extract frame: {result.stderr.decode()}")


def _composite_video(
    input_path: Path,
    patch_path: Path,
    overlay_x: int,
    overlay_y: int,
    output_path: Path,
    has_audio: bool,
    duration: float,
    on_progress: Callable[[str, int], None] | None = None,
) -> None:
    """Overlay the clean patch onto every frame of the video."""
    suffix = output_path.suffix.lower()

    # Select codec based on output format
    if suffix == ".webm":
        codec_args = ["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0"]
    else:
        # .mp4 and .mov both use H.264
        codec_args = [
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-movflags", "+faststart",
        ]

    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-i", str(patch_path),
        "-filter_complex", f"[0:v][1:v]overlay=x={overlay_x}:y={overlay_y}",
        *codec_args,
    ]

    if has_audio:
        cmd.extend(["-c:a", "copy"])

    cmd.extend(["-y", str(output_path)])

    # Run FFmpeg with progress parsing
    timeout = int(duration * 3) + 60
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    # Parse FFmpeg stderr for progress
    stderr_output = []
    try:
        for line in process.stderr:
            stderr_output.append(line)
            # Parse "time=00:00:04.00" from FFmpeg progress output
            time_match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
            if time_match and duration > 0 and on_progress:
                h, m, s = time_match.groups()
                current = int(h) * 3600 + int(m) * 60 + float(s)
                pct = min(int((current / duration) * 100), 99)
                on_progress(f"Processing video... {pct}%", pct)

        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        raise RuntimeError(f"FFmpeg timed out after {timeout}s")

    if process.returncode != 0:
        err = "".join(stderr_output[-10:])  # Last 10 lines
        raise RuntimeError(f"FFmpeg failed (exit {process.returncode}): {err}")

    if not output_path.exists():
        raise RuntimeError("FFmpeg produced no output file")
