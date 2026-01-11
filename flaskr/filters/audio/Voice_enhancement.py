# audio_filter.py

import numpy as np
from scipy.signal import butter, lfilter


def pre_emphasis(signal: np.ndarray, alpha: float = 0.97) -> np.ndarray:
    """
    Pre-emphasis filter:
    y[n] = x[n] - alpha * x[n-1]

    Supports mono (N,) and stereo (N, C)
    """
    signal = signal.astype(np.float32)

    if signal.ndim == 1:
        out = np.empty_like(signal)
        out[0] = signal[0]
        out[1:] = signal[1:] - alpha * signal[:-1]
        return out

    out = np.empty_like(signal)
    out[0, :] = signal[0, :]
    out[1:, :] = signal[1:, :] - alpha * signal[:-1, :]
    return out


def bandpass_filter(signal: np.ndarray,
                    fs: int,
                    lowcut: float = 300.0,
                    highcut: float = 3400.0,
                    order: int = 4) -> np.ndarray:
    """
    Butterworth band-pass filter for voice frequencies
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = min(highcut / nyquist, 0.99)

    b, a = butter(order, [low, high], btype="bandpass")

    if signal.ndim == 1:
        return lfilter(b, a, signal)

    filtered = np.zeros_like(signal)
    for ch in range(signal.shape[1]):
        filtered[:, ch] = lfilter(b, a, signal[:, ch])
    return filtered


def voice_enhancement(signal: np.ndarray,
                      fs: int,
                      alpha: float = 0.97) -> np.ndarray:
    """
    Full pipeline:
    Pre-emphasis → Band-pass
    """
    emphasized = pre_emphasis(signal, alpha)
    enhanced = bandpass_filter(emphasized, fs)

    # Normalize to avoid clipping
    peak = np.max(np.abs(enhanced))
    if peak > 1.0:
        enhanced = enhanced / peak

    return enhanced
