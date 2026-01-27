import subprocess
import os


def apply_upscaling(input_path: str,output_path: str,width: int,height: int) -> None:
    """
    Upscale video resolution using FFmpeg
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} does not exist")

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", f"scale={width}:{height}",
        "-c:a", "copy",
        output_path
    ]

    subprocess.run(command, check=True)
    print(f"Upscaled video saved to {output_path}")
def vf(params: dict) -> str:
    width = int(params.get("width", 1920))
    height = int(params.get("height", 1080))
    return f"scale={width}:{height}"


