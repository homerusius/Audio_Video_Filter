import numpy as np
from scipy.io import wavfile

def gain_compress(samples: np.ndarray, threshold: float = 0.2, ratio: float = 4.0) -> np.ndarray:
    """
    Simple gain compressor. Attenuates samples that exceed the threshold by a given ratio.
    """
    compressed = samples.copy().astype(float)
    # Normalize input to [-1, 1]
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        normalized = samples / max_val
    else:
        normalized = samples

    for i, x in np.ndenumerate(normalized):
        if x > threshold:
            normalized[i] = threshold + (x - threshold) / ratio
        elif x < -threshold:
            normalized[i] = -threshold + (x + threshold) / ratio

    # Scale back to original amplitude
    compressed = normalized * max_val
    return compressed

def process_file(input_path: str, output_path: str, threshold: float = 0.2, ratio: float = 4.0):
    """
    Load a WAV file, apply gain compression, and save the result.
    """
    fs, data = wavfile.read(input_path)
    # If stereo, process both channels separately
    if len(data.shape) > 1:
        channels = []
        for ch in range(data.shape[1]):
            channel_data = data[:, ch].astype(float) / 32768.0
            channel_processed = gain_compress(channel_data, threshold, ratio)
            channels.append((channel_processed * 32767).astype(np.int16))
        processed_data = np.column_stack(channels)
    else:
        normalized = data.astype(float) / 32768.0
        compressed = gain_compress(normalized, threshold, ratio)
        processed_data = (compressed * 32767).astype(np.int16)

    wavfile.write(output_path, fs, processed_data)
    print(f"Processed file saved to {output_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Apply gain compression to a WAV file.")
    parser.add_argument('input', help='Path to input WAV file')
    parser.add_argument('output', help='Path to output WAV file')
    parser.add_argument('--threshold', type=float, default=0.2, help='Compression threshold (0-1)')
    parser.add_argument('--ratio', type=float, default=4.0, help='Compression ratio (>1)')
    args = parser.parse_args()

    process_file(args.input, args.output, threshold=args.threshold, ratio=args.ratio)

