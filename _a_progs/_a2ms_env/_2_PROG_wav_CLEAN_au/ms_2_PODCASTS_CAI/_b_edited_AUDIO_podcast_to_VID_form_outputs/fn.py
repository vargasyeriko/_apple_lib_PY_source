#packages
from pydub import AudioSegment
from pydub.utils import mediainfo

import soundfile as sf
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.io import wavfile
from moviepy.editor import VideoClip, AudioFileClip

#------------------------------------------------------------------------------------------ CUTS AUDIO INTO PIECEs

def cut_and_export_audio(input_file, num_pieces, output_folder):
    # ^^^ path ^^^
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Read audio file
    data, sample_rate = sf.read(input_file)

    # Calculate the length of each piece
    piece_length = len(data) // num_pieces

    # Split and export the audio
    for i in range(num_pieces):
        start = i * piece_length
        end = (i + 1) * piece_length
        output_file = os.path.join(output_folder, f"piece_{i+1}.wav")
        # ^^^ path ^^^
        sf.write(output_file, data[start:end], sample_rate)
        
#------------------------------------------------------------------------------------------ makes video from sound
def make_vid_freq_graph():
    #background_video_path =  f"{desk_path}/
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.io import wavfile
    from moviepy.editor import VideoClip
    import imageio


    # Or, if you're using a frame from a video as a background
    # ^^^ path ^^^
    #background_video_path =  f"{desk_path}

    bg_image = imageio.imread(background_image_path)

    def make_frame(t):
        start_idx = int(t * fs)
        end_idx = int((t + 0.1) * fs)
        audio_slice = audio_data[start_idx:end_idx]

        fig, ax = plt.subplots()

        ax.set_ylim([-2**15, 2**15])
        ax.set_xlim([0, len(audio_slice)])

        ax.imshow(bg_image, aspect='auto', extent=[0, len(audio_slice), -2**15, 2**15])

        ax.plot(audio_slice, color=plot_color)
        ax.axis('off')

        # Additional decorations here...

        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)
        return frame

    fs, audio_data = wavfile.read(input_audio_path)
    video = VideoClip(make_frame, duration=(len(audio_data) / fs) - 0.1)
    video.write_videofile(output_video_path, fps=10)
    
    
    
    
    
    