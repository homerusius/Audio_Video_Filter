# video_filter.py

import numpy as np


def invert_colors(frame: np.ndarray) -> np.ndarray:
    """
    Color inversion filter.
    Works for:
    - RGB frames (MoviePy)
    - BGR frames (OpenCV)

    Assumes uint8 image.
    """
    if frame.dtype != np.uint8:
        frame = frame.astype(np.uint8)

    return 255 - frame
