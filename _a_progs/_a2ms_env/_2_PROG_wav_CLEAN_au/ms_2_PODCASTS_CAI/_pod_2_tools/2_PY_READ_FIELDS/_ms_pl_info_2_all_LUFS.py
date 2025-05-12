

import numpy as np
import pandas as pd
from pydub import AudioSegment
from pyloudnorm import Meter
from tqdm import tqdm

def compute_lufs_for_paths(paths):
    # Create a loudness meter (rate will be updated for each file)
    meter = Meter(rate=44100)  # default rate, will be changed for each file

    lufs_results = []

    # Wrap your loop with tqdm for a progress bar
    for file_path in tqdm(paths, desc="Computing LUFS", unit="file"):

        try:
            # Load the audio file using pydub
            audio = AudioSegment.from_file(file_path)

            # Convert audio to WAV format and get channels data
            samples = np.array(audio.get_array_of_samples())

            # Convert integer samples to floating point and normalize
            samples = samples / (2**15)

            # Check if stereo or mono
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
            else:
                samples = samples.reshape((-1, 1))

            # Update the sample rate of the meter
            meter.rate = audio.frame_rate

            # Compute LUFS
            loudness = meter.integrated_loudness(samples)

            lufs_results.append(round(loudness, 3))

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            lufs_results.append(None)  # Append None for the failed computation, keeping the list lengths in sync

    return lufs_results

# Example usage:

