
#----------------------------------------------------------------------------------------------------------------

import sounddevice as sd
from scipy.io import wavfile

def wav_play(filename):
    rate, data = wavfile.read(filename)
    sd.play(data, rate)
    sd.wait()  # Wait until the file is done playing
#----------------------------------------------------------------------------------------------------------------
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pyloudnorm as pyln

def wav_plot_3(file_path):
    # Load the audio file
    audio, sr = librosa.load(file_path, mono=True )

    # Compute LUFS
    meter = pyln.Meter(sr)  # create BS.1770 meter
    lufs = meter.integrated_loudness(audio)

    # Amplitude plot
    plt.figure(figsize=(15, 7))
    plt.subplot(3, 1, 1)
    librosa.display.waveshow(audio, sr=sr)
    plt.title(f'Amplitude - {file_path}')

    # LUFS plot
    plt.subplot(3, 1, 2)
    plt.bar(['LUFS'], [lufs])
    plt.title('Loudness (LUFS)')

    # Spectrogram
    plt.subplot(3, 1, 3)

    S = librosa.amplitude_to_db(np.abs(librosa.stft(audio)), ref=np.max)
    librosa.display.specshow(S, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Frequency Spectrogram')

    plt.tight_layout()
    plt.show()
#--------------------------------------------------------------------spectogram-------------------------------
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def wav_plot_spectrogram(file_path):
    """
    Plots the spectrogram of an audio file.

    Parameters:
    file_path (str): The path to the audio file.
    """
    # Load the audio file
    y, sr = librosa.load(file_path, sr=None)

    # Generate the spectrogram
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)

    # Plot the spectrogram
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.tight_layout()
    plt.show()



#----------------------------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd
from pydub import AudioSegment
from pyloudnorm import Meter

def compute_lufs_for_single_file(file_path):
    # Create a loudness meter (rate will be updated for the file)
    meter = Meter(rate=44100)  # default rate, will be changed for the file

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

        return round(loudness, 3)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None
#------------------------------------------------------------------------------------ GAIN

import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

def wav_analyze_gain(audio_file_path):
    # Load the audio file
    y, sr = librosa.load(audio_file_path, sr=None)

    # Visualize the waveform
    plt.figure(figsize=(10, 6))
    librosa.display.waveshow(y, sr=sr)
    plt.title("Waveform")
    plt.show()

    # Compute peak and RMS level
    peak_level = np.max(np.abs(y))
    rms_level = np.sqrt(np.mean(y**2))
    
    # Convert RMS to dBFS
    rms_dB = 20 * np.log10(rms_level)

    print(f"Peak Level (linear scale): {peak_level:.3f}")
    print(f"RMS Level (linear scale): {rms_level:.3f}")
    print(f"RMS Level (dBFS): {rms_dB:.2f} dB")

    # Check for clipping
    if peak_level >= 0.98: 
        print("Warning: The audio might be clipping!")
    elif rms_dB < -20: 
        print("Warning: The audio might be too soft for typical spoken content!")

    # Analyzing frequency bands
    D = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    power_spectrum = np.mean(D**2, axis=1)
    
    super_low_power = 20 * np.log10(np.mean(power_spectrum[freqs < 50]))
    low_power = 20 * np.log10(np.mean(power_spectrum[(freqs >= 50) & (freqs < 400)]))
    mid_power = 20 * np.log10(np.mean(power_spectrum[(freqs >= 400) & (freqs < 4000)]))
    high_power = 20 * np.log10(np.mean(power_spectrum[freqs >= 4000]))

    print("\nFrequency Band Power (dB):")
    print(f"Super Low (< 50Hz): {super_low_power:.2f} dB")
    print(f"Low (50Hz - 400Hz): {low_power:.2f} dB")
    print(f"Mid (400Hz - 4kHz): {mid_power:.2f} dB")
    print(f"High (> 4kHz): {high_power:.2f} dB")

    # Providing more context
    print("\nInterpretation:")
    if rms_dB < -20:
        print("- Your recording is softer than typical levels for spoken content. Consider amplifying.")
    else:
        print("- Your recording level is within the typical range for spoken content.")
    if peak_level >= 0.98:
        print("- Your recording might have clipping. This can lead to distortion. Reduce the volume or rerecording.")
    if super_low_power > -40:
        print("signfc power in low frequencies, which add unnecessary rumble or noise. Consider using a high-pass filter.")


#----------------------------------------------------------------------
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

def wav_freq_dist_pie_chart(audio_file_path):
    # Load the audio file
    y, sr = librosa.load(audio_file_path, sr=None)

    # Compute the power spectral density
    D = np.abs(librosa.stft(y))**2
    freqs = librosa.fft_frequencies(sr=sr)

    # Define the frequency bands
    bands = [(0, 50), (50, 400), (400, 4000)]
    power_distribution = []

    for low, high in bands:
        idx = np.logical_and(freqs >= low, freqs <= high)
        power = np.sum(D[idx])
        power_distribution.append(power)

    # Compute percentage distribution
    total_power = np.sum(power_distribution)
    percentages = [(power/total_power)*100 for power in power_distribution]
    labels = ['0-50Hz', '50-400Hz', '400-4000Hz']

    # Create a pie chart with a "donut" hole in the center
    wedges, texts = plt.pie(power_distribution, startangle=90, pctdistance=0.85, colors=['#FF9999', '#66B2FF', '#99FF99'])
    # Draw a circle in the center to make it a donut chart
    center_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(center_circle)

    # Legend table with percentages
    legend_labels = [f"{label}: {percentage:.2f}%" for label, percentage in zip(labels, percentages)]
    plt.legend(wedges, legend_labels, title="Frequency Bands", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(texts, size=0)  # Hide default pie labels

    plt.title("Frequency Power Distribution")
    plt.tight_layout()
    plt.show()

# ----------------
import wavio
import numpy as np
import matplotlib.pyplot as plt

def wav_freq_dist_plot(file_path):
    # Read the WAV file
    wav_obj = wavio.read(file_path)
    audio_data = wav_obj.data[:, 0]  # Assuming mono audio
    RATE = wav_obj.rate
    
    # Convert audio data to float and normalize it
    audio_data = audio_data.astype(np.float32, order='C') / 32767.0

    # Perform FFT
    sp = np.fft.fft(audio_data)
    freq = np.fft.fftfreq(len(audio_data), 1 / RATE)

    # Create subplots
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))

    # Low frequencies: 0-50Hz
    mask_low = np.where((freq >= 0) & (freq <= 50))
    axs[0].plot(freq[mask_low], np.abs(sp.real[mask_low]))
    axs[0].set_title('Low Frequencies (0-50 Hz)')
    axs[0].set_xlabel('Frequency [Hz]')
    axs[0].set_ylabel('Magnitude')
    axs[0].grid(True)

    # Human voice frequencies: 50-400Hz
    mask_voice = np.where((freq >= 50) & (freq <= 400))
    axs[1].plot(freq[mask_voice], np.abs(sp.real[mask_voice]))
    axs[1].set_title('Voice Frequencies (50-400 Hz)')
    axs[1].set_xlabel('Frequency [Hz]')
    axs[1].set_ylabel('Magnitude')
    axs[1].grid(True)

    # High frequencies: 400-2000Hz
    mask_high = np.where((freq >= 400) & (freq <= 4400))
    axs[2].plot(freq[mask_high], np.abs(sp.real[mask_high]))
    axs[2].set_title('High Frequencies (400-2000 Hz)')
    axs[2].set_xlabel('Frequency [Hz]')
    axs[2].set_ylabel('Magnitude')
    axs[2].grid(True)

    # Show the plot
    plt.tight_layout()
    plt.show()

# File path

#-------------- MANY AT ONCE
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def wav_audio_ana_6(file_path):
    """
    Analyzes and plots various aspects of an audio file.

    Parameters:
    file_path (str): The path to the audio file.
    """
    # Load the audio file
    y, sr = librosa.load(file_path)

    # Create a figure
    plt.figure(figsize=(12, 8))

    # Plot the waveform
    plt.subplot(3, 2, 1)
    librosa.display.waveshow(y, sr=sr)
    plt.title('Waveform')

    # Compute and plot the spectrogram
    plt.subplot(3, 2, 2)
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')

    # Compute and plot the spectral centroid and bandwidth
    plt.subplot(3, 2, 3)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    times = librosa.times_like(cent)
    plt.semilogy(times, cent.T, label='Spectral Centroid')
    plt.semilogy(times, bw.T, label='Spectral Bandwidth')
    plt.title('Spectral Centroid and Bandwidth')
    plt.legend()

    # Compute and plot the MFCCs
    plt.subplot(3, 2, 4)
    mfccs = librosa.feature.mfcc(y=y, sr=sr)
    librosa.display.specshow(mfccs, x_axis='time')
    plt.colorbar()
    plt.title('MFCC')

    # Plot the zero-crossing rate
    plt.subplot(3, 2, 5)
    zcr = librosa.feature.zero_crossing_rate(y)
    plt.plot(times, zcr[0], label='Zero-Crossing Rate')
    plt.title('Zero-Crossing Rate')

    # Plot the harmonic and percussive components
    plt.subplot(3, 2, 6)
    y_harm, y_perc = librosa.effects.hpss(y)
    librosa.display.waveshow(y_harm, sr=sr, alpha=0.25)
    librosa.display.waveshow(y_perc, sr=sr, color='r', alpha=0.5)
    plt.title('Harmonic and Percussive Components')

    plt.tight_layout()
    plt.show()

# Usage example:



# ----------- COMPARE n SPECTOGRAMS IN a FOLDER
import os
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

def direc_wav_compare_spct(directory):
    """Processes all .wav files in the specified directory and plots their spectrograms."""
    
    def read_wav_files():
        """Reads all .wav files in the directory."""
        wav_files = []
        for file in os.listdir(directory):
            if file.endswith('.wav'):
                wav_files.append(os.path.join(directory, file))
        return wav_files

    def plot_spectrogram(file_path):
        """Generates and plots a spectrogram for the given WAV file."""
        # Extracting filename for display
        file_name = os.path.basename(file_path)
        
        # Reading the file with librosa
        y, sr = librosa.load(file_path, sr=None)
        
        plt.figure(figsize=(10, 4))
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title(f'Spectrogram - {file_name}')
        plt.tight_layout()

    wav_files = read_wav_files()

    for file in wav_files:
        plot_spectrogram(file)

    plt.show()


















