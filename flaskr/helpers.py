from pathlib import Path
import subprocess
import numpy as np
from scipy.io import wavfile

from filters.audio import AUDIO_FILTERS
from filters.video import VIDEO_FILTERS

class FFmpegError(RuntimeError):
    pass

def _run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise FFmpegError((p.stderr or "")[-4000:])

def extract_audio(video_path: Path, wav_path: Path, fs: int = 48000) -> None:
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    _run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(fs),
        str(wav_path)
    ])

def _read_wav_float(path: Path) -> tuple[int, np.ndarray]:
    fs, data = wavfile.read(str(path))
    if np.issubdtype(data.dtype, np.integer):
        x = data.astype(np.float32) / float(np.iinfo(data.dtype).max)
    else:
        x = data.astype(np.float32)
    return fs, x

def _write_wav_float(path: Path, fs: int, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    x = np.clip(samples, -1.0, 1.0)
    wavfile.write(str(path), fs, (x * 32767).astype(np.int16))

def apply_audio_chain(wav_in: Path, wav_out: Path, config: dict) -> None:
    fs, samples = _read_wav_float(wav_in)
    for item in config.get("audio", []):
        name = item["name"]
        params = item.get("params", {}) or {}
        samples = AUDIO_FILTERS[name](samples, fs, params)
    _write_wav_float(wav_out, fs, samples)

def apply_video_and_mux(video_in: Path, audio_wav: Path, video_out: Path, config: dict) -> None:
    vf_parts = []
    for item in config.get("video", []):
        name = item["name"]
        params = item.get("params", {}) or {}
        vf_parts.append(VIDEO_FILTERS[name](params))

    cmd = ["ffmpeg", "-y", "-i", str(video_in), "-i", str(audio_wav)]
    if vf_parts:
        cmd += ["-vf", ",".join(vf_parts)]

    cmd += [
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(video_out)
    ]
    _run(cmd)

def apply_pipeline(input_video: Path, output_video: Path, config: dict, tmp_dir: Path) -> None:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    wav_in = tmp_dir / "audio_in.wav"
    wav_out = tmp_dir / "audio_out.wav"

    extract_audio(input_video, wav_in)
    apply_audio_chain(wav_in, wav_out, config)
    apply_video_and_mux(input_video, wav_out, output_video, config)
