
#--------------------------------------------------------------- 3a HP_mod_1
from scipy.signal import freqz, butter, lfilter
import matplotlib.pyplot as plt
import numpy as np
import librosa
import soundfile as sf

def wav_hp_mod_1(audio_file_path, cutoff_frequency, order=6):
    # Load the audio file
    y, sr = librosa.load(audio_file_path, sr=None)

    # Apply the high-pass filter using a butterworth filter of higher order
    b, a = butter(order, cutoff_frequency / (0.5 * sr), btype='high')
    y_hpf = lfilter(b, a, y)

    # Frequency response
    w, h = freqz(b, a, fs=sr)
    plt.plot(0.5 * sr * w / np.pi, np.abs(h), 'b')
    plt.axvline(cutoff_frequency, color='r')
    plt.xlim(0, 0.5 * sr)
    plt.title("High-pass filter frequency response (cutoff = %d Hz)" % cutoff_frequency)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Gain')
    plt.grid()
    plt.show()

    return y_hpf, sr




#--------------------------------------------------------------- 3b NR_mod_1
# NOISE REDUCTION

import librosa
import numpy as np
import scipy.signal

def wav_nr_mod_1(audio_file, noise_reduction_level=0.3, sensitivity=0.5):
    """
    Performs noise reduction on an audio file.
    
    :param audio_file: path to the audio file
    :param noise_reduction_level: float, the level of noise reduction (0-1)
    :param sensitivity: float, sensitivity of the noise reduction (0-1)
    :return: noise reduced audio array
    """

    # Load the audio file
    audio, sr = librosa.load(audio_file, sr=None)

    # Estimating noise
    noise_portion = audio[:int(0.5 * sr)]  # First half-second for noise profile
    noise_energy = np.mean(np.abs(noise_portion))

    # Applying noise gate threshold
    threshold = noise_energy * sensitivity

    # Noise reduction process
    noise_reduced_audio = []
    for sample in audio:
        if np.abs(sample) < threshold:
            noise_reduced_audio.append(sample * noise_reduction_level)
        else:
            noise_reduced_audio.append(sample)

    # Convert to numpy array
    noise_reduced_audio = np.array(noise_reduced_audio)

    return noise_reduced_audio

#------------------------------------------------------ 3b NR_mod_2
import librosa
import numpy as np
def wav_nr_mod_2(audio_file, noise_reduction_factor=0.3,frame_length=2048, hop_length=512):
    """
    Performs advanced noise reduction using spectral gating.
    :param audio_file: path to the audio file
    :param noise_reduction_factor: float, the factor by which noise is reduced :param frame_length: int, the length of each frame for STFT
    :param hop_length: int, the number of samples to shift for each frame in␣STFT
    :return: noise reduced audio array """
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None) # Short-time Fourier transform (STFT)
    stft_matrix = librosa.stft(y, n_fft=frame_length, hop_length=hop_length) # Compute the magnitude of the STFT
    stft_matrix_magnitude, stft_matrix_phase = librosa.magphase(stft_matrix)
    # Estimate the noise
    noise_profile = np.mean(stft_matrix_magnitude[:, :10], axis=1)
    noise_profile = noise_profile * noise_reduction_factor
    # Spectral gating
    noise_reduced_stft_magnitude = np.subtract(stft_matrix_magnitude,noise_profile[:, np.newaxis])
    noise_reduced_stft_magnitude = np.maximum(noise_reduced_stft_magnitude, np.zeros_like(noise_reduced_stft_magnitude))
    # Inverse STFT
    y_reduced_noise = librosa.istft(noise_reduced_stft_magnitude *stft_matrix_phase, hop_length=hop_length)
    return y_reduced_noise, sr
    # Usage

#-------------------- 3c NOISE GATE mod_1

import librosa
import numpy as np
import soundfile as sf

def wav_ng_mod_1(input_file_path, output_file_path, gate_threshold=-40.0, attack=0.01, release=0.1):
    """
    Applies a noise gate to the audio file and saves the output.

    :param input_file_path: path to the input audio file
    :param output_file_path: path to save the output audio file
    :param gate_threshold: dB threshold for noise gate
    :param attack: attack time in seconds
    :param release: release time in seconds
    :return: None
    """
    
    def noise_gate(audio, sr):
        """
        Apply a noise gate to the audio signal.
        """
        # Convert threshold from dB to amplitude
        threshold_amplitude = 10**(gate_threshold / 20)

        # Prepare attack and release coefficients
        attack_coeff = np.exp(-1/(sr * attack))
        release_coeff = np.exp(-1/(sr * release))

        # Envelope detection and gating
        envelope = 0
        gated_audio = np.zeros_like(audio)
        for i, sample in enumerate(audio):
            envelope = max(abs(sample), envelope * attack_coeff if abs(sample) < envelope else envelope * release_coeff)
            gated_audio[i] = sample if envelope > threshold_amplitude else 0

        return gated_audio

    # Load the audio file
    audio, sr = librosa.load(input_file_path, sr=None)

    # Apply noise gate
    audio_gated = noise_gate(audio, sr)

    # Save the gated audio
    sf.write(output_file_path, audio_gated, sr)



# END

#------------------------------------- 4a first Normalization 

import librosa
import numpy as np

def wav_norm_first(input_file_path, normalization_type='peak', target_level=-3.0):
    """
    Normalizes an audio file either using Peak or RMS normalization and returns the normalized audio data.

    :param input_file_path: Path to the input audio file
    :param normalization_type: Type of normalization ('peak' or 'rms')
    :param target_level: Target level in dB for normalization
    :return: Normalized audio data and sample rate
    """

    def peak_normalize(audio):
        """
        Normalize the audio using peak normalization.
        """
        peak = np.max(np.abs(audio))
        if peak == 0:
            return audio
        target_amplitude = 10 ** (target_level / 20)
        return audio * target_amplitude / peak

    def rms_normalize(audio):
        """
        Normalize the audio using RMS normalization.
        """
        rms = np.sqrt(np.mean(audio ** 2))
        if rms == 0:
            return audio
        target_amplitude = 10 ** (target_level / 20)
        return audio * target_amplitude / rms

    # Load the audio file
    audio, sr = librosa.load(input_file_path, sr=None)

    # Apply normalization based on the specified type
    if normalization_type == 'peak':
        audio_normalized = peak_normalize(audio)
    elif normalization_type == 'rms':
        audio_normalized = rms_normalize(audio)
    else:
        raise ValueError("Invalid normalization type. Choose 'peak' or 'rms'.")

    return audio_normalized, sr
#------------second NG


import librosa
import numpy as np
import soundfile as sf

def wav_ng_mod_2_pad(input_file_path, output_file_path, gate_threshold=-40.0, attack=0.01, release=0.1):
    """
    Applies a gentle noise gate to the audio file and saves the output.
    

    :param input_file_path: Path to the input audio file
    :param output_file_path: Path to save the output audio file
    :param gate_threshold: dB threshold for noise gate (lower value for gentle gating)
    :param attack: Attack time in seconds (shorter for quick response)
    :param release: Release time in seconds (longer for smoother tail-off)
    :return: None
    """

    def smooth_noise_gate(audio, sr):
        """
        Apply a gentle noise gate to the audio signal with gradual attack and release.
        """
        # Convert threshold from dB to amplitude
        threshold_amplitude = 10**(gate_threshold / 20)

        # Prepare attack and release coefficients
        attack_coeff = np.exp(-1/(sr * attack))
        release_coeff = np.exp(-1/(sr * release))

        # Envelope detection and smoothing
        envelope = 0
        gated_audio = np.zeros_like(audio)
        for i, sample in enumerate(audio):
            envelope = max(abs(sample), envelope * attack_coeff if abs(sample) < envelope else envelope * release_coeff)

            # Gentle gating
            gain = 1 if envelope > threshold_amplitude else (envelope / threshold_amplitude)
            gated_audio[i] = sample * gain

        return gated_audio

    # Load the audio file
    audio, sr = librosa.load(input_file_path, sr=None)

    # Apply gentle noise gate
    audio_gated = smooth_noise_gate(audio, sr)

    # Save the gated audio
    sf.write(output_file_path, audio_gated, sr)



#----------------------- comprssion and NORM for LUFS -19 to -22

import librosa
import numpy as np
import soundfile as sf
from scipy.signal import lfilter

def wav_comp_norm_lufs(input_file_path, output_file_path, threshold=-20.0, ratio=4.0, attack=0.01, release=0.1, target_lufs=-23.0):
    """
    Applies simple compression and adjusts gain to normalize to a target LUFS.

    :param input_file_path: path to the input audio file
    :param output_file_path: path to save the output audio file
    :param threshold: dB threshold for compression
    :param ratio: compression ratio
    :param attack: attack time in seconds
    :param release: release time in seconds
    :param target_lufs: target LUFS level for normalization
    :return: None
    """

    def simple_compressor(audio, sr, threshold, ratio, attack, release):
        """
        Apply simple compression to an audio signal.

        :param audio: NumPy array of audio samples
        :param sr: Sample rate of the audio
        :param threshold: Threshold for compression (dB)
        :param ratio: Compression ratio
        :param attack: Attack time in seconds
        :param release: Release time in seconds
        :return: Compressed audio
        """
        # Convert threshold from dB to amplitude
        threshold_amplitude = 10**(threshold / 20)

        # Prepare attack and release coefficients
        attack_coeff = np.exp(-1/(sr * attack))
        release_coeff = np.exp(-1/(sr * release))

        # Envelope detection and compression
        envelope = 0
        compressed_audio = np.zeros_like(audio)
        for i, sample in enumerate(audio):
            envelope = max(abs(sample), envelope * attack_coeff if abs(sample) < envelope else envelope * release_coeff)
            gain = 1 if envelope < threshold_amplitude else threshold_amplitude / envelope ** (1 - 1 / ratio)
            compressed_audio[i] = sample * gain

        return compressed_audio

    # Load the audio file
    audio, sr = librosa.load(input_file_path, sr=None)

    # Apply basic compression
    audio_compressed = simple_compressor(audio, sr, threshold, ratio, attack, release)

    # Calculate the required gain to achieve the target LUFS (simplified approach)
    # Note: This is a basic estimation and might not be accurate
    current_loudness = 20 * np.log10(np.mean(np.abs(audio_compressed)))
    gain = target_lufs - current_loudness

    # Apply the gain
    audio_normalized = audio_compressed * 10**(gain / 20)

    # Save the processed audio
    sf.write(output_file_path, audio_normalized, sr)

# Example usage
# compress_and_normalize_lufs('input_file.wav', 'output_file.wav', threshold=-20.0, ratio=4.0, attack=0.01, release=0.1, target_lufs=-23.0)



















