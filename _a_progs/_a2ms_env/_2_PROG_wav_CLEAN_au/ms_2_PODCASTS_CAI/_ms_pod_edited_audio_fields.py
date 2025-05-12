
##################################################################

##################################################################

##################################################################

##################################################################

##################################################################

##################################################################

##################################################################

##################################################################

##################################################################

import librosa
import numpy as np
import pandas as pd

def wav_get_fields(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path, mono=True)

    # Calculate duration in seconds and minutes
    duration_seconds = librosa.get_duration(y=y, sr=sr)
    duration_minutes = duration_seconds / 60.0

    # Convert the wav data to a numpy array
    wav_data = np.frombuffer(y, dtype=np.float32)

    # Calculate the maximum and minimum frequencies
    max_frequency = np.max(np.abs(np.fft.fft(wav_data)))
    min_frequency = np.min(np.abs(np.fft.fft(wav_data)))

    # Calculate the bit depth
    # Assuming 16-bit as librosa converts to float32 internally
    bit_depth = 16

    # Calculate the peak amplitude
    peak_amplitude = np.max(np.abs(wav_data))

    # Calculate the dynamic range
    dynamic_range = 20 * np.log10(np.max(np.abs(wav_data))) - 20 * np.log10(np.mean(np.abs(wav_data)))

    # Calculate the spectral content
    spectral_content = np.abs(np.fft.fft(wav_data))

    # Calculate the RMS Amplitude
    rms_amplitude = np.sqrt(np.mean(np.square(wav_data)))

    # Calculate the zero-crossing rate (commented out)
    # zero_crossing_rate = librosa.feature.zero_crossing_rate(y, frame_length=2048, hop_length=512)[0, 0]

    # Calculate the Mel-frequency cepstral coefficients (MFCCs) (commented out)
    # mfccs = librosa.feature.mfcc(y, sr=sr, n_mfcc=13)

    # Return a dictionary with the information
    return {
        "File": file_path,
        "Duration (s)": round(duration_seconds, 2),
        "Duration (min)": round(duration_minutes, 2),
        "Max frequency (Hz)": round(max_frequency, 2),
        "Min frequency (Hz)": round(min_frequency, 2),
        "Bit depth": bit_depth,
        "Sample rate": sr,
        "Peak amplitude": peak_amplitude,
        "Dynamic range": round(dynamic_range, 2),
        # "Spectral content": spectral_content.tolist(),
        # "RMS Amplitude": rms_amplitude,
        # Uncomment the following lines if needed
        # "Zero Crossing Rate": zero_crossing_rate,
        # "MFCCs": mfccs.tolist()
    }


