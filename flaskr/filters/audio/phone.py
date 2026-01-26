import numpy as np
from scipy.signal import butter, lfilter


def mono_enhancement(signal: np.ndarray,
                     side_attenuation: float = 0.3) -> np.ndarray:
    """
    Mono enhancement by side attenuation
    Works on stereo signals (N, 2)
    """
    if signal.ndim != 2 or signal.shape[1] != 2:
        return signal

    left = signal[:, 0]
    right = signal[:, 1]

    mid = (left + right) / 2.0
    side = (left - right) / 2.0

    side *= side_attenuation

    mono_left = mid + side
    mono_right = mid - side

    return np.stack((mono_left, mono_right), axis=1)


def bandpass_filter(signal: np.ndarray,
                    fs: int,
                    lowcut: float = 800.0,
                    highcut: float = 12000.0,
                    order: int = 4) -> np.ndarray:
    """
    Butterworth band-pass filter for phone effect
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = min(highcut / nyquist, 0.99)

    b, a = butter(order, [low, high], btype='bandpass')

    if signal.ndim == 1:
        return lfilter(b, a, signal)

    filtered = np.zeros_like(signal)
    for ch in range(signal.shape[1]):
        filtered[:, ch] = lfilter(b, a, signal[:, ch])

    return filtered


def phone_filter(signal: np.ndarray,
                 fs: int,
                 side_attenuation: float = 0.3) -> np.ndarray:
    """
    Phone audio filter:
    Mono enhancement + Band-pass filter
    """
    mono = mono_enhancement(signal, side_attenuation)
    filtered = bandpass_filter(mono, fs)

    peak = np.max(np.abs(filtered))
    if peak > 1.0:
        filtered = filtered / peak

    return filtered