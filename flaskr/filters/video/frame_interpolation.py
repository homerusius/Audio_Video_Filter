import subprocess
import os


def apply_frame_interpolation(input_path: str,
                              output_path: str,
                              target_fps: int) -> None:
    """
    Increase video frame rate using FFmpeg frame interpolation
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"{input_path} not found")

    command = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-vf', f'minterpolate=fps={target_fps}',
        '-c:a', 'copy',
        output_path
    ]

    subprocess.run(command, check=True)
    print(f"Interpolated video saved to {output_path}")