"""
Video filter registry.

The template uses these keys:
  grayscale, colorinvert, frameInterpolate, upscale

Each function returns an ffmpeg -vf fragment string.
"""

from .gray_scale import vf as grayscale
from .Color_Inversion import vf as colorinvert
from .frame_interpolation import vf as frameInterpolate
#from .upscaling import vf as upscale

VIDEO_FILTERS = {
    "grayscale": grayscale,
    "colorinvert": colorinvert,
    "frameInterpolate": frameInterpolate,
    #"upscale": upscale,
}
