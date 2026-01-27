import subprocess
import argparse
import os

def apply_grayscale(input_path: str, output_path: str) -> None:
    """
    Convert a video to grayscale using FFmpeg's hue filter.
    """
    command = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-vf', 'hue=s=0',
        '-c:a', 'copy',
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"Grayscale video saved to {output_path}")

def vf(params: dict) -> str:
    return "hue=s=0"

def generate_test_video(output_path: str, duration: float = 2.0, frame_rate: int = 30,
                        size: tuple = (320, 240)) -> None:
    """
    Generate a simple test video with moving colored rectangles using OpenCV.
    """
    import cv2
    import numpy as np

    width, height = size
    frames = int(duration * frame_rate)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, frame_rate, (width, height))
    for i in range(frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        color = (0, 255 * i // frames, 255 - 255 * i // frames)
        x = int(i * width / frames)
        cv2.rectangle(frame, (x, int(height/3)), (x + 50, int(2 * height/3)), color, -1)
        out.write(frame)
    out.release()
    print(f"Test video generated at {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Apply a grayscale filter to a video using FFmpeg.")
    parser.add_argument('input', nargs='?', help='Path to the input video file')
    parser.add_argument('output', nargs='?', help='Path for the output grayscale video file')
    parser.add_argument('--generate-sample', action='store_true',
                        help='Generate a test video instead of processing an existing one')
    parser.add_argument('--duration', type=float, default=2.0, help='Duration for sample video generation')
    args = parser.parse_args()

    if args.generate_sample:
        if not args.output:
            parser.error("Output path is required when generating a sample video.")
        generate_test_video(args.output, duration=args.duration)
    else:
        if not args.input or not args.output:
            parser.error("Both input and output paths are required when applying grayscale.")
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file {args.input} does not exist.")
        apply_grayscale(args.input, args.output)

if __name__ == '__main__':
    main()

