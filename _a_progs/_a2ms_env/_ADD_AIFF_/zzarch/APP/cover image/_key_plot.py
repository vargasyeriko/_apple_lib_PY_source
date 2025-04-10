
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

def _aiff_2409_coveriter_GET_save(df, output_folder: str, default_pic: str = None) -> None:
    """
    Iterates through a DataFrame of AIFF file paths and IDs, applies extract_aiff_cover,
    and renames the generated cover image to "cover_1_{id}.jpg" saved in the output folder.
    
    Parameters:
        df (pandas.DataFrame): A DataFrame with at least two columns:
            - "Path": containing the file path for an AIFF file.
            - "ID": a unique identifier used in output file naming.
        output_folder (str): Directory where the renamed cover images will be saved.
        default_pic (str): Optional file path for the default cover image if the AIFF file has no cover.
        
    Returns:
        None: The function processes each file, renames the generated cover image, and prints TQM messages.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Iterate over each row in the DataFrame
    for idx, row in df.iterrows():
        file_path = row["Path"]
        id_val = row["ID"]
        
        # Call the provided extract_aiff_cover function (DO NOT modify this function)
        result = extract_aiff_cover(file_path, pic=default_pic)
        
        if result:
            # The provided function writes output as base_name.jpg in the same folder as the AIFF file.
            base_name = os.path.splitext(file_path)[0]
            default_cover = f"{base_name}.jpg"
            
            # Construct the new cover image path with the naming convention "cover_1_{id}.jpg"
            new_cover_name = os.path.join(output_folder, f"cover_1_{id_val}.jpg")
            
            try:
                # Rename (or move) the default cover image file to the new cover image path
                os.rename(default_cover, new_cover_name)
                print(f"TQM: Cover image for ID {id_val} saved as {new_cover_name}")
            except Exception as e:
                print(f"Error renaming cover image for file {file_path}: {e}")
        else:
            print(f"TQM: Failed to process cover for file {file_path}")

# -----######-----######-----######-----######-----######-----######-----

# process cover art with circle 

# -----######-----######-----######-----######-----######-----######-----
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

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -----######-----######-----######-----######-----######-----######-----


# -----######-----######-----######-----######-----######-----######-----

# -----######-----######-----######-----######-----######-----######-----
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -----######-----######-----######-----######-----######-----######-----


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
