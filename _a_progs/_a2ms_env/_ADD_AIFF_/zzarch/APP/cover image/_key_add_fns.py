import os
from mutagen.aiff import AIFF
from mutagen.id3 import ID3, APIC
from PIL import Image, ImageOps
import io

def extract_aiff_cover(file_path, pic=None):
    # Check if the file is an AIFF
    if not file_path.lower().endswith('.aiff'):
        print("The file is not an AIFF.")
        return False

    try:
        # Load the AIFF file
        audio = AIFF(file_path)

        # Check if there is a cover image
        cover_tag = None
        cover_image = None

        for key, tag in audio.tags.items():
            if isinstance(tag, APIC):
                cover_tag = key
                cover_data = tag.data

                # Convert image data to a PIL image
                cover_image = Image.open(io.BytesIO(cover_data))
                break

        if cover_image is None:
            if pic is None:
                # Generate a black squared image if no cover is found and no path is provided
                cover_image = Image.new("RGB", (1000, 1000), "black")
                print("No cover found. Generated a black square image.")
            else:
                cover_image = Image.open(pic)
                print(f"Loaded default cover image from {pic}.")

        # Resize the image to 850x1000
        cover_image_resized = cover_image.resize((850, 1000))

        # Add black frames to the left and right
        frame_with_borders = ImageOps.expand(
            cover_image_resized, border=(95, 0, 155, 0), fill="black")

        # Add black frame to the bottom
        final_image = ImageOps.expand(
            frame_with_borders, border=(0, 0, 0, 400), fill="black")

        # Generate the output file path
        base_name = os.path.splitext(file_path)[0]
        output_file = f"{base_name}.jpg"

        # Save the resized image as JPG
        final_image.save(output_file, format="JPEG")
        print(f"Cover extracted, resized, framed, and saved as {output_file}")

        # Embed the resized cover back into the AIFF file
        with open(output_file, "rb") as img_file:
            cover_data = img_file.read()
            if cover_tag is not None:
                audio.tags[cover_tag].data = cover_data
            else:
                # Create a new APIC tag if none exists
                audio.tags.add(APIC(
                    encoding=3,         # UTF-8
                    mime='image/jpeg',  # MIME type
                    type=3,             # Cover (front)
                    desc='Cover',
                    data=cover_data
                ))
            audio.save()
            print(f"Resized and framed cover embedded back into the AIFF file.")

        return True

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False

# Example usage:
# extract_aiff_cover("/path/to/your/file.aiff")

#-----######-----###### IMPORT STATEMENTS -----######-----###### 
#-----######-----###### IMPORT STATEMENTS -----######-----###### 
import os
from PIL import Image, ImageDraw, ImageFont

#-----######-----###### FUNCTION: Resize & Process Cover Art -----######-----###### 
def _process_cover_art_with_circle(aiff_file_path, circle_size_ratio=0.2, position="top-right", 
                                   circle_color=(0, 0, 0, 255), text_color=(255, 255, 255, 255), 
                                   key="2A", text_scale=0.6):
    try:
        # Extract file name without extension
        base_name = os.path.splitext(os.path.basename(aiff_file_path))[0]
        cover_image_path = os.path.join(os.path.dirname(aiff_file_path), f"{base_name}.jpg")
        
        # Ensure the cover image exists
        if not os.path.isfile(cover_image_path):
            raise FileNotFoundError(f"No matching cover image found at {cover_image_path}")

        # Load and resize the cover image
        img = Image.open(cover_image_path).convert("RGBA")
        img = img.resize((1000, 1000), Image.ANTIALIAS)

        # Calculate circle size based on image dimensions
        img_width, img_height = img.size
        circle_size = int(min(img_width, img_height) * circle_size_ratio)

        # Create an overlay for the circle and text
        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Calculate circle position
        if position == "top-right":
            x, y = img_width - circle_size - 20, 20
        elif position == "bottom-right":
            x, y = img_width - circle_size - 20, img_height - circle_size - 20
        elif position == "top-left":
            x, y = 20, 20
        elif position == "bottom-left":
            x, y = 20, img_height - circle_size - 20
        else:
            raise ValueError("Invalid position specified. Use top-left, top-right, bottom-left, or bottom-right.")

        # Draw the solid Black circle
        draw.ellipse((x, y, x + circle_size, y + circle_size), fill=circle_color)

        # Add larger key text on top of the circle
        font_size = int(circle_size * text_scale)  # Text scale for bigger font
        try:
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Center text in the circle
        text_w, text_h = draw.textsize(key, font=font)
        text_x = x + (circle_size - text_w) / 2
        text_y = y + (circle_size - text_h) / 2
        draw.text((text_x, text_y), key, font=font, fill=text_color)

        # Merge cover art and overlay
        final_img = Image.alpha_composite(img, overlay)

        # Save the processed cover image
        output_image_path = os.path.join(os.path.dirname(aiff_file_path), f"{base_name}.jpg")
        final_img.convert("RGB").save(output_image_path, format='JPEG')

        print(f"Processed cover image saved at {output_image_path}")

    except Exception as e:
        print(f"Error processing cover art: {e}")


        
################## EMBED 

from PIL import Image
from mutagen.aiff import AIFF
from mutagen.id3 import APIC

def embed_cover_into_aiff(file_path, picture_path):
    """
    Embeds the specified picture into the AIFF file.
    If an APIC tag exists, it updates it; otherwise, it creates a new tag.
    """
    try:
        # Load the AIFF file
        audio = AIFF(file_path)

        # Read the image file
        with open(picture_path, "rb") as img_file:
            cover_data = img_file.read()

        cover_tag = None

        # Check if an APIC tag already exists
        for key, tag in audio.tags.items():
            if isinstance(tag, APIC):
                cover_tag = key
                break

        if cover_tag:
            # Update existing cover tag
            audio.tags[cover_tag].data = cover_data
            print("Updated existing cover tag.")
        else:
            # Create a new APIC tag if none exists
            audio.tags.add(APIC(
                encoding=3,         # UTF-8
                mime='image/jpeg',  # MIME type
                type=3,             # Cover (front)
                desc='Cover',
                data=cover_data
            ))
            print("Created a new cover tag.")

        # Save the updated AIFF file
        audio.save()
        print(f"Cover image successfully embedded in {file_path}")

    except Exception as e:
        print(f"Error embedding cover in {file_path}: {e}")

# Example usage:
# embed_cover_into_aiff("/path/to/your/file.aiff", "/path/to/your/image.jpg")
#################### Spectogram moon song age, and eclipse (intensity
#### good one 
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import librosa
import librosa.display

def _process_image_1012_GET_result(image_path, aiff_path, num, square_intensity, user_input, output_path):
    # Load the image
    img = Image.open(image_path).convert("RGB")
    width, height = img.size

    # Create the overlay for the bottom black area
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Calculate the bottom third height
    bottom_third_height = height // 3
    bottom_area_start = height - bottom_third_height

    # Element dimensions and padding
    padding = 20
    square_width = width // 10  # Adjusted size for the red square
    circle_radius = 50
    spectrogram_width = width // 3
    spectrogram_height = bottom_third_height - 2 * padding

    # Adjusted positions for better layout
    circle_x = padding + circle_radius + 50  # Moved right
    circle_y = bottom_area_start + padding + circle_radius + 20  # Moved lower
    square_left = circle_x + circle_radius + padding
    square_top = circle_y - circle_radius
    square_right = square_left + square_width
    square_bottom = square_top + square_width

    # 1. Add circle (yellow, blue, white) based on user input
    circle_color_map = {"ancient": "yellow", "old": "blue", "new": "white"}
    circle_color = circle_color_map.get(user_input.lower(), "white")
    draw.ellipse(
        [circle_x - circle_radius, circle_y - circle_radius,
         circle_x + circle_radius, circle_y + circle_radius],
        fill=circle_color, outline="black"
    )

    # 2. Add red square with light to strong intensity
    for i in range(square_intensity):
        color_intensity = int(255 * (i + 1) / square_intensity)
        draw.rectangle(
            [square_left, square_top, square_right, square_bottom],
            fill=(255, 0, 0, color_intensity)
        )
        square_left -= 1  # Slight gradient overlap to the left
        square_right -= 1

    # 3. Generate spectrogram from AIFF file
    y, sr = librosa.load(aiff_path, sr=None)
    plt.figure(figsize=(6, 2))
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    librosa.display.specshow(S_dB, sr=sr, x_axis="time", y_axis="mel", cmap="cool")
    plt.axis("off")

    # Save the spectrogram to paste on the image
    spectrogram_path = "/tmp/spectrogram.png"
    plt.savefig(spectrogram_path, bbox_inches="tight", pad_inches=0)
    plt.close()

    # Paste spectrogram onto the bottom third of the image with a frame
    spectrogram = Image.open(spectrogram_path).resize((spectrogram_width, spectrogram_height))
    frame_width = 5
    framed_spectrogram = Image.new("RGB", (spectrogram_width + 2 * frame_width, spectrogram_height + 2 * frame_width), "black")
    framed_spectrogram.paste(spectrogram, (frame_width, frame_width))

    spectrogram_x = (width - spectrogram_width) // 2  # Centered horizontally
    spectrogram_y = bottom_area_start + (bottom_third_height - spectrogram_height) // 2
    img.paste(framed_spectrogram, (spectrogram_x, spectrogram_y))

    # Merge overlay and image
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    # Convert the image back to RGB (JPEG does not support RGBA)
    img = img.convert("RGB")

    # Save the processed image
    img.save(output_path)

    return f"Image saved successfully at {output_path}"

############### LUFS
from PIL import Image, ImageDraw

def _overlay_circle_custom_0501_GET_image(input_string, image_path, circle_position=(0.5, 0.05), circle_diameter=100):
    """
    Function to overlay a colored circle corresponding to the last letter
    of an input string onto an image with customizable placement.
    
    Parameters:
        input_string: str - Input string where the last character is the relevant letter.
        image_path: str - Path to the input image.
        circle_position: tuple - Position of the circle as (x_fraction, y_fraction),
                                where (0.5, 0.05) centers horizontally and places
                                it near the top.
        circle_diameter: int - Diameter of the circle in pixels.
    """
    # Define the color mapping
    color_map = {
        'a': '#d3e5ff',  # Soft pastel blue (quiet)
        'b': '#92c6ff',  # Light blue
        'c': '#569aff',  # Moderate blue
        'd': '#0057e7',  # Bold blue
        'e': '#0039a6',  # Deep blue
        'f': '#001a6e',  # Intense navy (loud)
    }
    
    # Extract the last character after removing the first two
    letter = input_string[2:].lower()
    
    # Ensure the extracted letter is valid
    if letter not in color_map:
        raise ValueError("Input string must end with one of the following letters: 'a', 'b', 'c', 'd', 'e', 'f'.")
    
    # Open the image
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found at {image_path}")
    
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    
    # Circle parameters
    border_thickness = 5  # Thickness of the white border
    circle_color = color_map[letter]
    
    # Calculate circle position
    image_width, image_height = image.size
    circle_x = circle_position[0] * image_width - (circle_diameter / 2)
    circle_y = circle_position[1] * image_height - (circle_diameter / 2)
    
    # Draw the white border
    draw.ellipse(
        [
            (circle_x - border_thickness, circle_y - border_thickness),
            (circle_x + circle_diameter + border_thickness, circle_y + circle_diameter + border_thickness)
        ],
        fill="white"
    )
    
    # Draw the colored circle
    draw.ellipse(
        [
            (circle_x, circle_y),
            (circle_x + circle_diameter, circle_y + circle_diameter)
        ],
        fill=circle_color
    )
    
    # Save and show the image
    output_path = image_path#.replace(".jpg", "_overlay.jpg")
    image.save(output_path)
    #image.show()

