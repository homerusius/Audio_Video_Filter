"""
Audio filter registry.

The template uses these keys:
  gainCompressor, voiceEnhancement, denoiseDelay, phone, car
"""

from .gain_compression import gain_compress
from .Voice_enhancement import voice_enhancement

# wrappers to normalize interface to: apply(samples, fs, params) -> samples
def _gainCompressor_apply(samples, fs, params):
    # your teammate's function uses threshold/ratio; map template params if present
    # if your UI uses dB thresholds, adapt later; this works for now.
    threshold = float(params.get("gainCompressorThreshold", params.get("threshold", 0.2)))
    ratio = float(params.get("ratio", 4.0))
    return gain_compress(samples, threshold=threshold, ratio=ratio)

def _voiceEnhancement_apply(samples, fs, params):
    alpha = float(params.get("preemphasisAlpha", 0.97))
    # teammate function signature: voice_enhancement(signal, fs, alpha=..., cutoff=...)
    cutoff = float(params.get("highPassFilter", 0.0))
    return voice_enhancement(samples, fs=fs, alpha=alpha, cutoff=cutoff)

from .phone import apply as phone_apply
from .car import apply as car_apply

AUDIO_FILTERS = {
    "gainCompressor": _gainCompressor_apply,
    "voiceEnhancement": _voiceEnhancement_apply,
    "phone": phone_apply,
    "car": car_apply,
}
