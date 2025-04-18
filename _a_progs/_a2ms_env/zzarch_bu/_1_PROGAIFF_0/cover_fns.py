
def key_plot():
    for i in df.index:  # Loop over each row index
        key_song = df.loc[i, "key_dj"]
        set_plus = df.loc[i, "Key_Up"]
        set_minus = df.loc[i, "Key_Down"]
        set_scale = df.loc[i, "Mood_Shifter"]
        jaws_mix = df.loc[i, "Jaw_s_Mix"]
        id_ = df.loc[i, "ID"]
        
    # 0_FNS: Define primary functions with TQM bar integration
    # -----######----- CORE FUNCTIONS -----######-----
        def create_donut_plot(inner_color, outer_colors, set_plus, set_minus, set_scale, jaws_mix):
            """
            Creates a donut plot with an inner circle and an outer circle with highlighted partitions.
            
            Parameters:
            - inner_color: Color of the inner circle.
            - outer_colors: List of colors for the outer circle.
            - set_plus: Number and letter (e.g., "12A") to mark with a '+'.
            - set_minus: Number and letter (e.g., "2A") to mark with a '-'.
            - set_scale: Number and letter (e.g., "4B") to mark with an 'X'.
            - jaws_mix: Number and letter (e.g., "7B") to mark with a 'J' for jaws mix.
            
            TQM BAR: Ensure proper DataFrame processing integration if needed.
            """
            # Parse the inputs for numbers and letters
            set_plus_num, set_plus_letter = int(set_plus[:-1]), set_plus[-1]
            set_minus_num, set_minus_letter = int(set_minus[:-1]), set_minus[-1]
            set_scale_num, set_scale_letter = int(set_scale[:-1]), set_scale[-1]
            jaws_mix_num, jaws_mix_letter = int(jaws_mix[:-1]), jaws_mix[-1]
            
            # Color mappings for letters (you can extend this mapping if desired)
            color_map = {'A': 'red', 'B': 'blue'}
            
            # Adjust rotation so the first color fully faces up
            adjusted_rotation_angle = 90 - (360 / 24)  # Slight adjustment to center the first partition
            
            # Highlight partitions dynamically
            highlighted_colors = []
            for i in range(12):
                number = 12 - i if i != 0 else 12
                # Check for each special marker; order is assumed distinct.
                if number == set_plus_num:
                    highlighted_colors.append(color_map.get(set_plus_letter, 'black'))
                elif number == set_minus_num:
                    highlighted_colors.append(color_map.get(set_minus_letter, 'black'))
                elif number == set_scale_num:
                    highlighted_colors.append(color_map.get(set_scale_letter, 'black'))
                elif number == jaws_mix_num:
                    highlighted_colors.append(color_map.get(jaws_mix_letter, 'black'))
                else:
                    highlighted_colors.append(outer_colors[i])
            
            # Create figure and axes
            import matplotlib.pyplot as plt  # Ensure self-contained function
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect="equal"))
            
            # Plot the inner circle
            ax.pie([1],  # Single partition for the inner circle
                   radius=0.9,
                   labels=None,
                   colors=[inner_color],
                   startangle=0,
                   wedgeprops=dict(width=0.9, edgecolor='w'))
            
            # Plot the outer circle with adjusted rotation
            outer_radius = 1.05
            ax.pie([1] * 12,  # Exactly 12 partitions
                   radius=outer_radius,
                   labels=None,  # No labels
                   colors=highlighted_colors,
                   startangle=adjusted_rotation_angle,
                   wedgeprops=dict(width=outer_radius - 0.8, edgecolor='w'))
            
            # Remove axes for a cleaner look
            ax.set(aspect="equal")
            plt.axis('off')  # Hide axes
            
            return ax, adjusted_rotation_angle, outer_radius  # Return axes and parameters for further customization
        
        def add_clock_numbers_with_styles(ax, adjusted_rotation_angle, outer_radius, rotation_offset, 
                                          set_plus, set_minus, set_scale, key_song, jaws_mix):
            """
            Adds clock numbers (12 to 1) with customized styles based on the input for '+' (set_plus), '-' (set_minus), 
            'X' (set_scale), and 'J' (jaws_mix), including the associated letters. The key_song is placed in the center.
            
            Parameters:
            - ax: The axes object returned from the donut plot.
            - adjusted_rotation_angle: The starting angle for the plot.
            - outer_radius: The radius of the outer circle used for positioning numbers.
            - rotation_offset: Additional angle (in degrees) to rotate the numbers.
            - set_plus: Number and letter (e.g., "12A") to mark with a '+'.
            - set_minus: Number and letter (e.g., "2A") to mark with a '-'.
            - set_scale: Number and letter (e.g., "4B") to mark with an 'X'.
            - key_song: String to be placed in the center of the circle.
            - jaws_mix: Number and letter (e.g., "7B") to mark with a 'J' for jaws mix.
            
            TQM BAR: Ensure compatibility when processing DataFrame columns.
            """
            # Parse the inputs for numbers and letters
            set_plus_num, set_plus_letter = int(set_plus[:-1]), set_plus[-1]
            set_minus_num, set_minus_letter = int(set_minus[:-1]), set_minus[-1]
            set_scale_num, set_scale_letter = int(set_scale[:-1]), set_scale[-1]
            jaws_mix_num, jaws_mix_letter = int(jaws_mix[:-1]), jaws_mix[-1]
            
            angle_step = 360 / 12  # Step size for each partition
            import numpy as np  # Ensure self-contained function
            angles = np.arange(0, 360, angle_step) + adjusted_rotation_angle + rotation_offset  # Adjust angles as needed
            text_radius = outer_radius - 0.12  # Position text slightly inward from the outer edge
            
            # Overlay clock numbers (12 to 1) with their respective annotations
            for i, angle in enumerate(angles):
                number = 12 - i if i != 0 else 12
                x = text_radius * np.cos(np.radians(angle))
                y = text_radius * np.sin(np.radians(angle))
            
                # Start with an empty annotation string
                symbol = ""
                if number == set_plus_num:
                    symbol += f"\n+{set_plus_letter}"
                if number == set_minus_num:
                    symbol += f"\n-{set_minus_letter}"
                if number == set_scale_num:
                    symbol += f"\n*{set_scale_letter}"
                if number == jaws_mix_num:
                    symbol += f"\nJ{jaws_mix_letter}"
            
                # Add text with white font for visibility
                ax.text(x, y, f"{number}{symbol}", ha='center', va='center', fontsize=16, weight='bold', color='white')
            
            # Place key_song in the center of the circle with prominent styling
            ax.text(0, 0, key_song, ha='center', va='center', fontsize=102, weight='bold', color='white')
            
        # -----######----- END OF CORE FUNCTIONS -----######-----
        # !#!#!#!#! RUNNING STATEMENTS !#!#!#!#!
        import matplotlib.pyplot as plt
        
        # Input variables
        inner_circle_color = '#000000'  # Black for the inner circle
        outer_circle_colors = [
            "#2E2E2E",  # Dark Gray
            "#282828",  # Charcoal Gray
            "#242424",  # Jet Black
            "#1F1F1F",  # Dark Gunmetal
            "#1B1B1B",  # Onyx
            "#181818",  # Eerie Black
            "#141414",  # Black Olive
            "#101010",  # Smoky Black
            "#0D0D0D",  # Outer Space Black
            "#0A0A0A",  # Licorice
            "#070707",  # Rich Black
            "#000000"   # Pure Black
        ]
        
     # Main key song string to be placed in the center
        rotation_offset = 15
        
        # Create the donut plot with jaws_mix integrated for highlighting
        ax, adjusted_rotation_angle, outer_radius = create_donut_plot(
            inner_circle_color, outer_circle_colors, set_plus, set_minus, set_scale, jaws_mix
        )
        
        # Add clock numbers with styles along with key_song annotation, including jaws_mix along the circle
        add_clock_numbers_with_styles(
            ax, adjusted_rotation_angle, outer_radius, rotation_offset, 
            set_plus, set_minus, set_scale, key_song, jaws_mix
        )
        
        # Save the plot with a dynamic filename (ensure variable 'num' is defined or replace it appropriately)
        num = 1  # Example index value for filename customization
        plt.savefig(f"{direc_jpg}key_plot{id_}.png", format="png", dpi=300)
        
        # If you want to display the plot, uncomment the next line:
        print('DONE')
        #plt.show()


# -----######-----######-----######-----######-----######-----######-----

# 0_FNS: Core Function Definition
# -----######-----######----- CORE FUNCTION -----######-----######
# This function processes every PNG image in the input directory by replacing white/near-white pixels 
# with transparency and then overwrites the original image in the same folder.
import os
from PIL import Image

def _png_2409_wbrem_GET_overwrite_imgs(input_dir: str, tolerance: int = 200) -> None:
    """
    Processes each PNG image in the input directory by converting near-white pixels to transparent
    and overwrites each image in the same folder.
    
    Parameters:
        input_dir (str): Directory containing the PNG images.
        tolerance (int): Brightness threshold for detecting near-white pixels (default is 200).
    
    Returns:
        None. The function overwrites the processed images in the input directory.
    """
    # Iterate over all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(input_dir, filename)
            try:
                # Open the image and convert it to RGBA to handle transparency
                image = Image.open(file_path).convert("RGBA")
                data = image.getdata()
                new_data = []

                # Process each pixel: if the average of R, G, B is greater than tolerance, set it transparent
                for item in data:
                    brightness = sum(item[:3]) / 3  # Average brightness calculation
                    if brightness > tolerance:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                
                # Update the image with the new pixel data and overwrite the original file
                image.putdata(new_data)
                image.save(file_path, "PNG")
                print(f"TQM: Processed and overwritten image {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----

####  extract COVER
# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
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

# 0_FNS: Core Iteration Function Definition
# -----######-----######----- CORE FUNCTION -----######-----######
# This function iterates through a DataFrame that contains AIFF file paths in a 'Path' column 
# and corresponding IDs in an 'ID' column. It applies the provided extract_aiff_cover function on each file,
# then renames the output cover image to the pattern "cover_1_{id}.jpg" and writes it into the output folder.

import os
# 0_FNS
import os
import glob
import pandas as pd

# ###########################################################################
# ########## CORE FUNCTION: _aiff_2409_coveriter_GET_save ###################
# ###########################################################################
# 0_FNS
import os
import shutil
import pandas as pd

# ###########################################################################
# ########## CORE FUNCTION: _aiff_2409_coveriter_GET_save ###################
# ###########################################################################
# ###########################################################################
# ########## CORE FUNCTION: _aiff_2409_coveriter_GET_save ###################
# ###########################################################################
def _aiff_2409_coveriter_GET_save(df, direc_jpg: str, default_pic: str = None) -> None:
    """
    Extracts and saves AIFF cover as 'cover_1_{ID}.jpg' in direc_jpg.
    Overwrites existing covers. Compatible across volumes (no cross-device errors).

    Parameters:
        df (pd.DataFrame): Must contain 'Path' and 'ID' columns
        direc_jpg (str): Folder to store final output cover images
        default_pic (str): Optional fallback if no embedded cover
    """
    os.makedirs(direc_jpg, exist_ok=True)

    for _, row in df.iterrows():
        file_path = row["Path"]
        id_val = row["ID"]

        temp_cover = os.path.splitext(file_path)[0] + ".jpg"
        final_cover = os.path.join(direc_jpg, f"cover_1_{id_val}.jpg")

        if os.path.exists(final_cover):
            os.remove(final_cover)

        result = extract_aiff_cover(file_path, pic=default_pic)

        if result and os.path.exists(temp_cover):
            try:
                shutil.move(temp_cover, final_cover)
                print(f"TQM ✅ Cover saved: {final_cover}")
            except Exception as e:
                print(f"❌ ERROR moving cover: {e}")
        else:
            # If no cover extracted, fallback black image
            try:
                img = Image.new("RGB", (1000, 1400), "black")
                img.save(final_cover, format="JPEG")
                print(f"🖤 Default black cover saved as fallback: {final_cover}")
            except Exception as e:
                print(f"❌ ERROR saving fallback black image: {e}")


# def _aiff_2409_coveriter_GET_save(df, output_folder: str, default_pic: str = None) -> None:
#     """
#     Iterates through a DataFrame of AIFF file paths and IDs, applies extract_aiff_cover,
#     and renames the generated cover image to "cover_1_{id}.jpg" saved in the output folder.
    
#     Parameters:
#         df (pandas.DataFrame): A DataFrame with at least two columns:
#             - "Path": containing the file path for an AIFF file.
#             - "ID": a unique identifier used in output file naming.
#         output_folder (str): Directory where the renamed cover images will be saved.
#         default_pic (str): Optional file path for the default cover image if the AIFF file has no cover.
        
#     Returns:
#         None: The function processes each file, renames the generated cover image, and prints TQM messages.
#     """
#     # Ensure output folder exists
#     os.makedirs(output_folder, exist_ok=True)
    
#     # Iterate over each row in the DataFrame
#     for idx, row in df.iterrows():
#         file_path = row["Path"]
#         id_val = row["ID"]
        
#         # Call the provided extract_aiff_cover function (DO NOT modify this function)
#         result = extract_aiff_cover(file_path, pic=default_pic)
        
#         if result:
#             # The provided function writes output as base_name.jpg in the same folder as the AIFF file.
#             base_name = os.path.splitext(file_path)[0]
#             default_cover = f"{base_name}.jpg"
            
#             # Construct the new cover image path with the naming convention "cover_1_{id}.jpg"
#             new_cover_name =f"{output_folder}/cover_1_{id_val}.jpg"
            
#             try:
#                 # Rename (or move) the default cover image file to the new cover image path
#                 os.rename(default_cover, new_cover_name)
#                 print(f"TQM: Cover image for ID {id_val} saved as {new_cover_name}")
#             except Exception as e:
#                 print(f"Error renaming cover image for file {file_path}: {e}")
#         else:
#             print(f"TQM: Failed to process cover for file {file_path}")

# -----######-----######-----######-----######-----######-----######-----

# process cover art with circle 
#-----######-----###### IMPORT STATEMENTS -----######-----######
import os
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

#-----######-----###### FUNCTION: Process Cover Art with Circle -----######-----######
def _img_2409_process_coverart_GET_output(aiff_file_path, jpg_album_path, 
                                          circle_size_ratio=0.2, position="top-right", 
                                          circle_color=(0, 0, 0, 255), 
                                          text_color=(255, 255, 255, 255), 
                                          variable="2A", text_scale=0.6):
    """
    Process a cover art image by embedding a colored circle with variable text.
    
    Parameters:
      aiff_file_path (str): Path to the original AIFF file (for reference/logging).
      jpg_album_path (str): Path to the corresponding album cover (jpg) image.
      circle_size_ratio (float): Ratio of the circle's diameter to the minimum image dimension.
      position (str): Position for the circle ('top-left', 'top-right', 'bottom-left', or 'bottom-right').
      circle_color (tuple): RGBA tuple for the circle's color.
      text_color (tuple): RGBA tuple for the text color.
      variable (str): The text to display on the circle (e.g., a BPM value or any other variable).
      text_scale (float): Scale factor (relative to the circle size) for the font size.
      
    Returns:
      None (The processed image is saved back to the provided jpg_album_path).
    """
    try:
        # Ensure the cover image exists
        if not os.path.isfile(jpg_album_path):
            raise FileNotFoundError(f"No matching cover image found at {jpg_album_path}")

        # Load and resize the cover image using the LANCZOS filter (replacing ANTIALIAS)
        img = Image.open(jpg_album_path).convert("RGBA")
        img = img.resize((1000, 1000), Image.LANCZOS)
        
        # Calculate circle dimensions
        img_width, img_height = img.size
        circle_size = int(min(img_width, img_height) * circle_size_ratio)
        margin = 20  # Margin from the image border

        # Create an overlay for the circle and text
        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Determine circle position based on the specified option
        if position == "top-right":
            x, y = img_width - circle_size - margin, margin
        elif position == "bottom-right":
            x, y = img_width - circle_size - margin, img_height - circle_size - margin
        elif position == "top-left":
            x, y = margin, margin
        elif position == "bottom-left":
            x, y = margin, img_height - circle_size - margin
        else:
            raise ValueError("Invalid position specified. Use top-left, top-right, bottom-left, or bottom-right.")

        # Draw the solid circle on the overlay
        draw.ellipse((x, y, x + circle_size, y + circle_size), fill=circle_color)

        # Set font size relative to the circle and load the font
        font_size = int(circle_size * text_scale)
        try:
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Compute text bounding box (using textbbox) and derive width and height
        bbox = draw.textbbox((0, 0), variable, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = x + (circle_size - text_w) / 2
        text_y = y + (circle_size - text_h) / 2
        draw.text((text_x, text_y), variable, font=font, fill=text_color)

        # Merge the overlay with the cover art and save the final image
        final_img = Image.alpha_composite(img, overlay)
        final_img.convert("RGB").save(jpg_album_path, format='JPEG')
        print(f"Processed cover image saved at {jpg_album_path}")

    except Exception as e:
        print(f"Error processing cover art for {aiff_file_path}: {e}")

#-----######-----###### FUNCTION: Process DataFrame Cover Art with TQDM -----######-----######
def _img_2409_process_df_coverart_GET_output(df, 
                                             circle_size_ratio=0.2, 
                                             position="top-right", 
                                             circle_color=(0, 0, 0, 255), 
                                             text_color=(255, 255, 255, 255), 
                                             text_scale=0.6,
                                             text_column="dominant_bpm"):
    """
    Processes cover art for each row in the DataFrame using the 'Path', 'Path_jpg_album',
    and a user-specified column for the overlay text.
    
    You can specify which DataFrame column holds the text to be added to the cover image by setting
    the 'text_column' parameter. If 'text_column' is None or an empty string, no text is drawn.
    
    Parameters:
      df (DataFrame): DataFrame containing at least the following columns:
                      - 'Path': the AIFF file path (for reference/logging).
                      - 'Path_jpg_album': the corresponding jpg cover art image path.
                      - (Optional) A column specified by text_column which holds the text (e.g., BPM).
      circle_size_ratio (float): Ratio of the circle's diameter to the minimum image dimension.
      position (str): Position for the circle ('top-left', 'top-right', 'bottom-left', or 'bottom-right').
      circle_color (tuple): RGBA tuple for the circle's color.
      text_color (tuple): RGBA tuple for the text color.
      text_scale (float): Scale factor (relative to the circle size) for the font size.
      text_column (str, optional): Name of the DataFrame column that contains the text to overlay.
                                   Default is "dominant_bpm". If set to None or empty, no text is added.
      
    Returns:
      None (Processes and saves each cover art image with the specified parameters).
    """
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing Cover Art"):
        # Determine the variable text from the given column; if not provided, use an empty string.
        if text_column and text_column in row:
            variable_text = str(row[text_column])
        else:
            variable_text = ""
            
        kwargs = {
            "aiff_file_path": row['Path'],
            "jpg_album_path": row['Path_jpg_album'],
            "circle_size_ratio": circle_size_ratio,
            "position": position,
            "circle_color": circle_color,
            "text_color": text_color,
            "variable": variable_text,
            "text_scale": text_scale
        }
        _img_2409_process_coverart_GET_output(**kwargs)

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----

#-----######-----###### IMPORT STATEMENTS -----######-----######
import os
from PIL import Image
from tqdm import tqdm

#-----######-----###### FUNCTION: Overlay Key Image onto Album -----######-----######
def _img_2409_overlay_key_GET_output(aiff_file_path, jpg_album_path, jpg_key_path,
                                     resize_factor=0.265, 
                                     position_right_cm=-0.232, position_top_cm=-0.59, 
                                     dpi=300):
    """
    Overlays a PNG image (key image) onto a JPG album cover.
    
    Parameters:
      aiff_file_path (str): Path to the original AIFF file (for reference/logging).
      jpg_album_path (str): Path to the corresponding album cover (jpg) image.
      jpg_key_path (str): Path to the PNG overlay (key) image.
      resize_factor (float): Scale factor to resize the overlay image.
      position_right_cm (float): Distance (in cm) from the right edge of the background. 
                                 Negative values shift the overlay rightward.
      position_top_cm (float): Distance (in cm) from the top edge of the background.
                               Negative values push the overlay off (or closer to) the top.
      dpi (int): Dots per inch used for converting centimeters to pixels.
      
    Returns:
      None (The modified album image is saved back to the jpg_album_path.)
    """
    try:
        # Ensure both images exist.
        if not os.path.isfile(jpg_album_path):
            raise FileNotFoundError(f"No album cover found at {jpg_album_path}")
        if not os.path.isfile(jpg_key_path):
            raise FileNotFoundError(f"No key overlay image found at {jpg_key_path}")
        
        # Load the background album image and the overlay (key) image
        background = Image.open(jpg_album_path)
        overlay = Image.open(jpg_key_path)
        
        # Resize the overlay using the specified factor
        overlay_resized = overlay.resize(
            (int(overlay.width * resize_factor), int(overlay.height * resize_factor))
        )
        
        # Function to convert centimeters to pixels based on DPI
        cm_to_pixels = lambda cm: int(cm * dpi / 2.54)
        
        # Calculate offsets for overlay positioning
        x_offset = background.width - overlay_resized.width - cm_to_pixels(position_right_cm)
        y_offset = cm_to_pixels(position_top_cm)
        
        # Ensure the overlay image is in RGBA mode to support transparency
        if overlay_resized.mode != 'RGBA':
            overlay_resized = overlay_resized.convert('RGBA')
        
        # Paste the overlay onto the background using the overlay as a mask
        background.paste(overlay_resized, (x_offset, y_offset), overlay_resized)
        
        # Save the modified album image (overwriting the original file)
        background.save(jpg_album_path)
        print(f"Overlay applied and saved for album at {jpg_album_path}")
        
    except Exception as e:
        print(f"Error overlaying key for {aiff_file_path}: {e}")

#-----######-----###### FUNCTION: Process DataFrame for Key Overlay -----######-----######
def _img_2409_overlay_df_key_GET_output(df,
                                        resize_factor=0.265,
                                        position_right_cm=-0.232, position_top_cm=-0.59,
                                        dpi=300):
    """
    Iterates over each row of the DataFrame and overlays a key PNG (from 'Path_jpg_key')
    onto the corresponding album JPG (from 'Path_jpg_album').
    
    Expected DataFrame columns:
      - 'Path': AIFF file path (for logging/reference)
      - 'Path_jpg_album': Path to the album cover (jpg)
      - 'Path_jpg_key': Path to the key overlay (png)
      
    Parameters:
      df (DataFrame): DataFrame with the required image path columns.
      resize_factor (float): Scale factor to resize the overlay image.
      position_right_cm (float): Distance from the right edge (cm) for overlay positioning.
      position_top_cm (float): Distance from the top edge (cm) for overlay positioning.
      dpi (int): Dots per inch used for converting centimeters to pixels.
      
    Returns:
      None (Overlays are applied iteratively and album images are saved with the key overlay).
    """
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Overlaying Key Images"):
        kwargs = {
            "aiff_file_path": row['Path'],
            "jpg_album_path": row['Path_jpg_album'],
            "jpg_key_path": row['Path_jpg_key'],
            "resize_factor": resize_factor,
            "position_right_cm": position_right_cm,
            "position_top_cm": position_top_cm,
            "dpi": dpi
        }
        _img_2409_overlay_key_GET_output(**kwargs)

# -----######-----######-----######-----######-----######-----######-----
#### LUFS

#-----######-----###### IMPORT STATEMENTS -----######-----######
import os
from PIL import Image, ImageDraw
from tqdm import tqdm

#-----######-----###### FUNCTION: Overlay Blue Circle Based on LUFS Code -----######-----######
def _overlay_circle_custom_0501_GET_image(input_string, image_path, circle_position=(0.5, 0.05), circle_diameter=100):
    """
    Overlays a colored circle (with blue tones) onto an image. The circle's color is determined by 
    the last letter (after skipping the first two characters) of an input string.
    
    Parameters:
        input_string (str): A string from which the last letter (after removing first two characters)
                            determines the blue tone.
        image_path (str): Path to the image on which to overlay the circle.
        circle_position (tuple): Fractional (x, y) position for the circle's center relative to the image dimensions.
        circle_diameter (int): Diameter of the circle in pixels.
    
    Raises:
        ValueError: If the extracted letter is not one of 'a', 'b', 'c', 'd', 'e', or 'f'.
        FileNotFoundError: If the image file is not found.
        
    Returns:
        None (The image file is overwritten with the new overlay).
    """
    # Define the blue tone color mapping
    color_map = {
        'a': '#d3e5ff',  # Soft pastel blue (quiet)
        'b': '#92c6ff',  # Light blue
        'c': '#569aff',  # Moderate blue
        'd': '#0057e7',  # Bold blue
        'e': '#0039a6',  # Deep blue
        'f': '#001a6e',  # Intense navy (loud)
    }
    
    # Extract the relevant letter from the input string (skip the first two characters)
    letter = input_string[2:].lower()  # if input_string is "Lue", then letter becomes "e"
    if letter not in color_map:
        raise ValueError("Input string must end with one of the following letters: 'a', 'b', 'c', 'd', 'e', 'f'.")
    
    # Open the target image
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found at {image_path}")
    
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    border_thickness = 5  # Thickness of the white border
    circle_color = color_map[letter]  # Determine the blue tone from the letter
    
    # Calculate the circle's top-left coordinate based on fractional position and the diameter
    image_width, image_height = image.size
    circle_x = circle_position[0] * image_width - (circle_diameter / 2)
    circle_y = circle_position[1] * image_height - (circle_diameter / 2)
    
    # Draw the white border for contrast
    draw.ellipse(
        [
            (circle_x - border_thickness, circle_y - border_thickness),
            (circle_x + circle_diameter + border_thickness, circle_y + circle_diameter + border_thickness)
        ],
        fill="white"
    )
    
    # Draw the colored circle inside the white border
    draw.ellipse(
        [
            (circle_x, circle_y),
            (circle_x + circle_diameter, circle_y + circle_diameter)
        ],
        fill=circle_color
    )
    
    # Save the modified image (overwrites original)
    image.save(image_path)
    print(f"Overlay applied on image: {image_path}")

#-----######-----###### FUNCTION: Process DataFrame for LUFS Overlay -----######-----######
def _overlay_df_circle_custom_0501_GET_image(df, circle_position=(0.5, 0.05), circle_diameter=100, ms_LUFS_column='ms_LUFS_code'):
    """
    Iterates over each row of the DataFrame, fetching the LUFS code from the given column and 
    applying the overlay function to the corresponding album image.
    
    Parameters:
        df (DataFrame): DataFrame containing at least the following columns:
                        - 'Path_jpg_album': Path to the album cover image (JPG).
                        - ms_LUFS_column (default 'ms_LUFS_code'): Column that contains the LUFS code string.
        circle_position (tuple): Fractional (x, y) position for the overlay circle relative to the image.
        circle_diameter (int): Diameter of the overlay circle in pixels.
        ms_LUFS_column (str): Name of the DataFrame column that contains the LUFS code.
    
    Returns:
        None (Each album image is overwritten with the new overlay).
    """
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Overlaying LUFS Circles"):
        input_string = str(row[ms_LUFS_column])
        image_path = row['Path_jpg_album']
        _overlay_circle_custom_0501_GET_image(input_string, image_path, circle_position=circle_position, circle_diameter=circle_diameter)

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----
#### frequency CLIP
# 0_FNS
# -----######----- Core Importable Functions -----######-----

import librosa
import librosa.display
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# -----######-----###### UPDATED CLIPPING DETECTION FUNCTION -----######-----######
def detect_top_clipping(audio_data, sample_rate, threshold=0.0, top_n=110):
    """
    Detects the top N clipping events in an audio signal based on a dBFS threshold.
    
    Parameters:
    - audio_data: numpy array, the audio samples (e.g., from librosa.load)
    - sample_rate: int, the sampling rate of the audio signal
    - threshold: float, the dBFS threshold to detect clipping (default: 0.0 dBFS)
    - top_n: int, the number of top clipping events to return
    
    Returns:
    - top_clipping_times: list, times (in seconds) of the top N clipping events
    - top_clipping_amplitudes: list, corresponding amplitudes of the top N clipping events
    """
    # Convert the threshold from dBFS to amplitude
    amplitude_threshold = 10 ** (threshold / 20.0)
    
    # Find samples exceeding the threshold
    clipped_indices = np.where(np.abs(audio_data) >= amplitude_threshold)[0]
    clipped_amplitudes = audio_data[clipped_indices]
    
    # Sort by absolute amplitude, descending
    sorted_indices = np.argsort(np.abs(clipped_amplitudes))[::-1]
    top_indices = clipped_indices[sorted_indices[:top_n]]
    top_amplitudes = clipped_amplitudes[sorted_indices[:top_n]]
    
    # Convert sample indices to times
    top_clipping_times = top_indices / sample_rate
    
    return top_clipping_times, top_amplitudes

# -----######-----###### VISUALIZATION FUNCTION -----######-----######
def visualize_clipping_and_print_top(file_path, threshold=0.0, top_n=10, duration=None):
    """
    Visualizes the clipping events for an audio file and prints the top clipping events.
    
    Parameters:
    - file_path: str, the path to the audio file.
    - threshold: float, clipping threshold in dBFS.
    - top_n: int, number of top clipping events to detect.
    - duration: float or None, duration (in seconds) up to which the audio file is analyzed.
    """
    # Load the audio file with a fixed duration
    y, sr = librosa.load(file_path, sr=None, duration=duration)
    
    # Detect the top clipping events
    top_clipping_times, top_clipping_amplitudes = detect_top_clipping(y, sr, threshold=threshold, top_n=top_n)
    
    # Create a DataFrame for clipping data
    clipping_data = pd.DataFrame({
        "Time (s)": top_clipping_times,
        "Amplitude": top_clipping_amplitudes
    })
    
    # Print clipping information
    print("\nTop Clipping Events (dBFS > 0.0):")
    print(clipping_data)
    
    # Compute spectrogram (STFT)
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=512))
    D = librosa.amplitude_to_db(S, ref=np.max)
    
    # Plot the spectrogram
    fig, ax = plt.subplots(figsize=(14, 3))  # Wider for better clarity
    img = librosa.display.specshow(D, sr=sr, hop_length=512, x_axis='time', y_axis=None, cmap='coolwarm', ax=ax)

    # Add thick red vertical lines for the top clipping moments
    for time in top_clipping_times:
        ax.axvline(x=time, color='red', linestyle='-', linewidth=3, alpha=1.0)

    # Add minute labels to the x-axis
    total_duration = len(y) / sr  # Total duration in seconds
    num_minutes = int(np.ceil(total_duration / 60))
    minute_ticks = np.arange(0, num_minutes + 1) * 60  # Tick locations in seconds
    ax.set_xticks(minute_ticks)
    ax.set_xticklabels([f"min {i}" for i in range(len(minute_ticks))], fontsize=12, fontweight='bold', color='black')

    # Add a color bar for amplitude levels
    cbar = fig.colorbar(img, ax=ax, orientation='vertical', fraction=0.02, pad=0.04)
    cbar.set_ticks([np.min(D), (np.min(D) + np.max(D)) / 2, np.max(D)])
    cbar.ax.set_yticklabels(['-1', '0', '1'], fontsize=12, fontweight='bold')  # Big labels for clipping reference

    # Apply tight layout to ensure everything fits without overlapping
    plt.tight_layout()
    # plt.show() is commented out to allow saving without blocking the iteration

# -----######-----###### NEW ITERATION FUNCTION TO GENERATE AND SAVE CLIPPING PLOTS -----######-----######
def _audio_2409_i2_GET_generate_clipping_plots(df, threshold=-0.005, top_n=100, duration=600, save_directory="/Users/yerik/Downloads/try_py_AIFF"):
    """
    Iterates over the DataFrame, generates clipping plots for each audio file, and saves them as JPEG images.
    
    The DataFrame is expected to have the following columns:
        - 'Path': the path to the audio file.
        - 'ID': a unique identifier for the file (used in the filename). If not present, the DataFrame index is used.
    
    Parameters:
    - df: pandas DataFrame containing audio file paths and identifiers.
    - threshold: float, clipping threshold in dBFS (default: -0.005).
    - top_n: int, number of top clipping events to detect (default: 100).
    - duration: int or float, duration in seconds to analyze from the audio (default: 600 seconds).
    - save_directory: str, directory path where the plot images will be saved.
    """
    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Generating clipping plots"):
        file_path = row['Path']
        identifier = row.get('ID', idx)  # Use the 'ID' column if available, else fallback to index
        try:
            # Generate the visualization (this prints data and creates the plot)
            visualize_clipping_and_print_top(file_path, threshold=threshold, top_n=top_n, duration=duration)
            # Save the plot with naming scheme "clip_plot{ID}.jpg"
            save_path = f"{save_directory}/clip_plot{identifier}.jpg"
            plt.savefig(save_path, format='jpg', dpi=300)
            print(f"Saved plot for {file_path} as {save_path}")
            plt.clf()  # Clear the current figure for the next file
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")



# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -----######-----######-----######-----######-----######-----######-----
## embed frequ
# 0_FNS
# -----######----- Core Importable Functions -----######-----

from PIL import Image
from tqdm import tqdm

def layer_images(base_path, layer_path, output_path, scale=0.8, padding=10, align_horizontal="center", align_vertical="bottom", offset_x=0, offset_y=0):
    """
    Layers a rectangular image (Image A) on top of a square background image (Image B).
    
    Parameters:
        base_path (str): File path to the base square image.
        layer_path (str): File path to the layer rectangular image.
        output_path (str): File path to save the resulting image.
        scale (float): Scale factor for resizing the layer image (default: 0.8).
        padding (int): Padding between the layer image and edges of the base image (default: 10).
        align_horizontal (str): Horizontal alignment: "left", "center", or "right" (default: "center").
        align_vertical (str): Vertical alignment: "top", "middle", or "bottom" (default: "bottom").
        offset_x (int): Horizontal offset in pixels for fine-tuning position (default: 0).
        offset_y (int): Vertical offset in pixels for fine-tuning position (default: 0).
    """
    # Load the images
    base_img = Image.open(base_path)
    layer_img = Image.open(layer_path)

    # Resize the layer image
    layer_width = int(base_img.width * scale)
    layer_height = int(layer_img.height * (layer_width / layer_img.width))
    layer_img = layer_img.resize((layer_width, layer_height), Image.ANTIALIAS)

    # Calculate horizontal position
    if align_horizontal == "left":
        x_pos = padding
    elif align_horizontal == "center":
        x_pos = (base_img.width - layer_width) // 2
    elif align_horizontal == "right":
        x_pos = base_img.width - layer_width - padding
    else:
        raise ValueError("align_horizontal must be 'left', 'center', or 'right'.")

    # Calculate vertical position
    if align_vertical == "top":
        y_pos = padding
    elif align_vertical == "middle":
        y_pos = (base_img.height - layer_height) // 2
    elif align_vertical == "bottom":
        y_pos = base_img.height - layer_height - padding
    else:
        raise ValueError("align_vertical must be 'top', 'middle', or 'bottom'.")

    # Apply offsets
    x_pos += offset_x
    y_pos += offset_y

    # Create a new image to combine both
    combined_img = base_img.copy()
    combined_img.paste(layer_img, (x_pos, y_pos), layer_img if layer_img.mode == 'RGBA' else None)

    # Save the output
    combined_img.save(output_path)
    print(f"Image saved to {output_path}")

# -----######-----###### NEW ITERATION FUNCTION FOR EMBEDDING CLIPPING PLOTS INTO ALBUM COVERS -----######-----######
def _img_2409_i3_GET_embed_clipping_on_album(df):
    """
    Iterates over the DataFrame, layers the clipping plot onto the album cover image,
    and saves the resulting image by overwriting the album cover image.
    
    Expects the DataFrame to have:
      - 'Path_jpg_album': path to the base album cover (square image).
      - 'Path_jpg_clip': path to the clipping plot image (rectangular image).
    
    The resulting image is saved to the same path as the album cover.
    
    Uses the following settings (DO NOT CHANGE ANYTHING):
      - scale=1.04
      - padding=80
      - align_horizontal="center"
      - align_vertical="bottom"
      - offset_x=-5
      - offset_y=100
    """
    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Embedding clipping into album cover"):
        base_image = row['Path_jpg_album']
        layer_image = row['Path_jpg_clip']
        output_image = base_image  # Overwrite the base album cover with the combined image
        try:
            layer_images(
                base_path=base_image, 
                layer_path=layer_image, 
                output_path=output_image,
                scale=1.04,
                padding=80,
                align_horizontal="center",
                align_vertical="bottom",
                offset_x=-5,
                offset_y=100
            )
        except Exception as e:
            print(f"Error processing row {idx}: {e}")






# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -----######-----######-----######-----######-----######-----######-----
## EMBED
# 0_FNS
# -----######----- Core Importable Functions -----######-----
from tqdm import tqdm
from mutagen.aiff import AIFF
from mutagen.id3 import APIC

def embed_cover_into_aiff(file_path, picture_path):
    """
    Embeds the specified picture into the AIFF file.
    If an APIC tag exists, it updates it; otherwise, creates a new tag.
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
            print(f"Updated existing cover tag for {file_path}")
        else:
            # Create a new APIC tag since none exists
            audio.tags.add(APIC(
                encoding=3,         # UTF-8
                mime='image/jpeg',  # MIME type
                type=3,             # Cover (front)
                desc='Cover',
                data=cover_data
            ))
            print(f"Created a new cover tag for {file_path}")

        # Save the updated AIFF file
        audio.save()
        print(f"Cover image successfully embedded in {file_path}")

    except Exception as e:
        print(f"Error embedding cover in {file_path}: {e}")


def _aiff_2409_i1_GET_embed_aiff_covers(df):
    """
    Iterates through the DataFrame, embedding cover images into AIFF files.
    Expects the DataFrame to have the following columns:
      - 'Path': File paths for AIFF files.
      - 'Path_jpg_album': File paths for the corresponding cover images.
      
    This function uses a tqdm progress bar to indicate progress.
    """
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Embedding covers"):
        embed_cover_into_aiff(row['Path'], row['Path_jpg_album'])

# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----
# -----######-----######-----######-----######-----######-----######-----

# dynamic donout 
# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*


################ bu
# ## bu 
# # 0_FNS: Define primary functions with TQM bar integration
# # -----######----- CORE FUNCTIONS -----######-----
# def create_donut_plot(inner_color, outer_colors, set_plus, set_minus, set_scale, jaws_mix):
#     """
#     Creates a donut plot with an inner circle and an outer circle with highlighted partitions.
    
#     Parameters:
#     - inner_color: Color of the inner circle.
#     - outer_colors: List of colors for the outer circle.
#     - set_plus: Number and letter (e.g., "12A") to mark with a '+'.
#     - set_minus: Number and letter (e.g., "2A") to mark with a '-'.
#     - set_scale: Number and letter (e.g., "4B") to mark with an 'X'.
#     - jaws_mix: Number and letter (e.g., "7B") to mark with a 'J' for jaws mix.
    
#     TQM BAR: Ensure proper DataFrame processing integration if needed.
#     """
#     # Parse the inputs for numbers and letters
#     set_plus_num, set_plus_letter = int(set_plus[:-1]), set_plus[-1]
#     set_minus_num, set_minus_letter = int(set_minus[:-1]), set_minus[-1]
#     set_scale_num, set_scale_letter = int(set_scale[:-1]), set_scale[-1]
#     jaws_mix_num, jaws_mix_letter = int(jaws_mix[:-1]), jaws_mix[-1]
    
#     # Color mappings for letters (you can extend this mapping if desired)
#     color_map = {'A': 'red', 'B': 'blue'}
    
#     # Adjust rotation so the first color fully faces up
#     adjusted_rotation_angle = 90 - (360 / 24)  # Slight adjustment to center the first partition
    
#     # Highlight partitions dynamically
#     highlighted_colors = []
#     for i in range(12):
#         number = 12 - i if i != 0 else 12
#         # Check for each special marker; order is assumed distinct.
#         if number == set_plus_num:
#             highlighted_colors.append(color_map.get(set_plus_letter, 'black'))
#         elif number == set_minus_num:
#             highlighted_colors.append(color_map.get(set_minus_letter, 'black'))
#         elif number == set_scale_num:
#             highlighted_colors.append(color_map.get(set_scale_letter, 'black'))
#         elif number == jaws_mix_num:
#             highlighted_colors.append(color_map.get(jaws_mix_letter, 'black'))
#         else:
#             highlighted_colors.append(outer_colors[i])
    
#     # Create figure and axes
#     import matplotlib.pyplot as plt  # Ensure self-contained function
#     fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect="equal"))
    
#     # Plot the inner circle
#     ax.pie([1],  # Single partition for the inner circle
#            radius=0.9,
#            labels=None,
#            colors=[inner_color],
#            startangle=0,
#            wedgeprops=dict(width=0.9, edgecolor='w'))
    
#     # Plot the outer circle with adjusted rotation
#     outer_radius = 1.05
#     ax.pie([1] * 12,  # Exactly 12 partitions
#            radius=outer_radius,
#            labels=None,  # No labels
#            colors=highlighted_colors,
#            startangle=adjusted_rotation_angle,
#            wedgeprops=dict(width=outer_radius - 0.8, edgecolor='w'))
    
#     # Remove axes for a cleaner look
#     ax.set(aspect="equal")
#     plt.axis('off')  # Hide axes
    
#     return ax, adjusted_rotation_angle, outer_radius  # Return axes and parameters for further customization

# def add_clock_numbers_with_styles(ax, adjusted_rotation_angle, outer_radius, rotation_offset, 
#                                   set_plus, set_minus, set_scale, key_song, jaws_mix):
#     """
#     Adds clock numbers (12 to 1) with customized styles based on the input for '+' (set_plus), '-' (set_minus), 
#     'X' (set_scale), and 'J' (jaws_mix), including the associated letters. The key_song is placed in the center.
    
#     Parameters:
#     - ax: The axes object returned from the donut plot.
#     - adjusted_rotation_angle: The starting angle for the plot.
#     - outer_radius: The radius of the outer circle used for positioning numbers.
#     - rotation_offset: Additional angle (in degrees) to rotate the numbers.
#     - set_plus: Number and letter (e.g., "12A") to mark with a '+'.
#     - set_minus: Number and letter (e.g., "2A") to mark with a '-'.
#     - set_scale: Number and letter (e.g., "4B") to mark with an 'X'.
#     - key_song: String to be placed in the center of the circle.
#     - jaws_mix: Number and letter (e.g., "7B") to mark with a 'J' for jaws mix.
    
#     TQM BAR: Ensure compatibility when processing DataFrame columns.
#     """
#     # Parse the inputs for numbers and letters
#     set_plus_num, set_plus_letter = int(set_plus[:-1]), set_plus[-1]
#     set_minus_num, set_minus_letter = int(set_minus[:-1]), set_minus[-1]
#     set_scale_num, set_scale_letter = int(set_scale[:-1]), set_scale[-1]
#     jaws_mix_num, jaws_mix_letter = int(jaws_mix[:-1]), jaws_mix[-1]
    
#     angle_step = 360 / 12  # Step size for each partition
#     import numpy as np  # Ensure self-contained function
#     angles = np.arange(0, 360, angle_step) + adjusted_rotation_angle + rotation_offset  # Adjust angles as needed
#     text_radius = outer_radius - 0.12  # Position text slightly inward from the outer edge
    
#     # Overlay clock numbers (12 to 1) with their respective annotations
#     for i, angle in enumerate(angles):
#         number = 12 - i if i != 0 else 12
#         x = text_radius * np.cos(np.radians(angle))
#         y = text_radius * np.sin(np.radians(angle))
    
#         # Start with an empty annotation string
#         symbol = ""
#         if number == set_plus_num:
#             symbol += f"\n+{set_plus_letter}"
#         if number == set_minus_num:
#             symbol += f"\n-{set_minus_letter}"
#         if number == set_scale_num:
#             symbol += f"\n*{set_scale_letter}"
#         if number == jaws_mix_num:
#             symbol += f"\nJ{jaws_mix_letter}"
    
#         # Add text with white font for visibility
#         ax.text(x, y, f"{number}{symbol}", ha='center', va='center', fontsize=16, weight='bold', color='white')
    
#     # Place key_song in the center of the circle with prominent styling
#     ax.text(0, 0, key_song, ha='center', va='center', fontsize=119, weight='bold', color='white')
    
# # -----######----- END OF CORE FUNCTIONS -----######-----
# # !#!#!#!#! RUNNING STATEMENTS !#!#!#!#!
# import matplotlib.pyplot as plt

# # Input variables
# inner_circle_color = '#000000'  # Black for the inner circle
# outer_circle_colors = [
#     "#2E2E2E",  # Dark Gray
#     "#282828",  # Charcoal Gray
#     "#242424",  # Jet Black
#     "#1F1F1F",  # Dark Gunmetal
#     "#1B1B1B",  # Onyx
#     "#181818",  # Eerie Black
#     "#141414",  # Black Olive
#     "#101010",  # Smoky Black
#     "#0D0D0D",  # Outer Space Black
#     "#0A0A0A",  # Licorice
#     "#070707",  # Rich Black
#     "#000000"   # Pure Black
# ]

# # Define styling variables
# set_plus = "11A"
# set_minus = "9A"
# set_scale = "1B"
# jaws_mix = "5A"   # New variable for jaws_mix with its own numeric and letter marker
# key_song = "10A"  # Main key song string to be placed in the center
# rotation_offset = 15

# # Create the donut plot with jaws_mix integrated for highlighting
# ax, adjusted_rotation_angle, outer_radius = create_donut_plot(
#     inner_circle_color, outer_circle_colors, set_plus, set_minus, set_scale, jaws_mix
# )

# # Add clock numbers with styles along with key_song annotation, including jaws_mix along the circle
# add_clock_numbers_with_styles(
#     ax, adjusted_rotation_angle, outer_radius, rotation_offset, 
#     set_plus, set_minus, set_scale, key_song, jaws_mix
# )

# # Save the plot with a dynamic filename (ensure variable 'num' is defined or replace it appropriately)
# num = 1  # Example index value for filename customization
# #plt.savefig(f"/Users/yerik/Downloads/try_py_AIFF/key_plot{ID}.png", format="png", dpi=300)

# # If you want to display the plot, uncomment the next line:
# plt.show()
