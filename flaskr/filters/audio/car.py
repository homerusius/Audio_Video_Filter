import numpy as np
from scipy.signal import butter, lfilter


def stereo_enhancement(signal: np.ndarray,side_gain: float = 1.5) -> np.ndarray:
    """
    Stereo enhancement by side amplification
    """
    if signal.ndim != 2 or signal.shape[1] != 2:
        return signal

    left = signal[:, 0]
    right = signal[:, 1]

    mid = (left + right) / 2.0
    side = (left - right) / 2.0

    side *= side_gain

    out_left = mid + side
    out_right = mid - side

    return np.stack((out_left, out_right), axis=1)


def lowpass_filter(signal: np.ndarray,fs: int,cutoff: float = 10000.0,order: int = 4) -> np.ndarray:
    """
    Butterworth low-pass filter
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist

    b, a = butter(order, normal_cutoff, btype='low')

    if signal.ndim == 1:
        return lfilter(b, a, signal)

    filtered = np.zeros_like(signal)
    for ch in range(signal.shape[1]):
        filtered[:, ch] = lfilter(b, a, signal[:, ch])

    return filtered


def car_filter(signal: np.ndarray,fs: int,side_gain: float = 1.5) -> np.ndarray:
    """
    Car audio filter:
    Stereo enhancement + Low-pass filter
    """
    enhanced = stereo_enhancement(signal, side_gain)
    filtered = lowpass_filter(enhanced, fs)

    peak = np.max(np.abs(filtered))
    if peak > 1.0:
        filtered = filtered / peak

    return filtered