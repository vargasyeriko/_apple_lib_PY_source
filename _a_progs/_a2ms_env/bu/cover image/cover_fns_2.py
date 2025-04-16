# 0_FNS
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# ###########################################################################
# ########## CORE FUNCTION: _bpm_2610_i3_GET_partialdonut_bpmdynamic   ########
# ###########################################################################
def _bpm_2610_i3_GET_partialdonut_bpmdynamic(df: pd.DataFrame, save_dir: str = "images") -> None:
    """
    Iterates over the provided DataFrame and saves an individual PNG for each row.
    Each PNG contains a donut chart that illustrates the BPM dynamic percentage as 
    a colored wedge (based on 'bpm_consistency_cat') with the remainder of the circle transparent.
    
    The donut is only partially complete in reference to the provided percentage.
    The figure is saved as a PNG with a transparent background and no extra labels.
    
    The PNG files are saved using the value from the 'ID' column in the DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame with columns:
                           - 'bpm_consistency': numeric value between 0 and 100.
                           - 'bpm_consistency_cat': dynamic category label (e.g., 'D_0', 'D_1', 'D_3', 'D_6', 'D_9'),
                             with D_0 being least dynamic (yellow) and D_9 super dynamic (dark gray).
                           - 'ID': unique identifier for each row/song used for file naming.
        save_dir (str): Directory where the PNG images will be saved. Defaults to "images".
    """
    # Define a cohesive color mapping using a Material Design–inspired gradient.
    color_mapping = {
         'D_0': "#FFEB3B",  # Bright yellow (original)
    'D_1': "#E6D435",  # 90% brightness of D_0
    'D_3': "#CCBC2F",  # 80% brightness of D_0
    'D_6': "#998D23",  # 60% brightness of D_0
    'D_9': "#665E17"    # Near-black
    }
    
    # Ensure the save directory exists.
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if not save_dir.endswith(os.sep):
        save_dir += os.sep

    # ------------------ TQM BAR: Starting donut generation with 50% thinner ring ------------------
    # Iterate over each row in the DataFrame.
    for _, row in df.iterrows():
        dynamic_value = row['bpm_consistency']  # Percentage value (0 to 100)
        dynamic_cat = row['bpm_consistency_cat']
        
        # Compute the segments: filled part equals dynamic percentage; remainder (to 100) is transparent.
        segments = [dynamic_value, 100 - dynamic_value]
        colors = [color_mapping.get(dynamic_cat, '#9E9E9E'), (0, 0, 0, 0)]
        
        # Create figure and axis.
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.axis('off')  # Remove axes for a clean image.
        
        # Draw the donut chart using wedgeprops to create a hole in the center.
        # Updated wedge width to 0.15 (i.e., 50% thinner than the original 0.3)
        ax.pie(
            segments, 
            colors=colors, 
            startangle=90, 
            counterclock=False, 
            wedgeprops={'width': 0.15, 'edgecolor': 'none'}
        )
        
        # Use the value in the 'ID' column as the file name.
        file_name = f"{save_dir}bpm_bar_dyn_{row['ID']}.png"
        plt.savefig(file_name, bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close(fig)
        print(f"Saved: {file_name}")
    # ------------------ TQM BAR: Donut generation completed ------------------
# ########## END OF CORE FUNCTION ###########################################
# ########## END OF CORE FUNCTION ###########################################
# _bpm_2610_i3_GET_partialdonut_bpmdynamic(df, save_dir="images")
# df['Path_png_bar_dyn'] = f'{direc_jpg}' + 'bpm_bar_dyn_' + df['ID'] + '.png'
# df


# 0_FNS
import os
from PIL import Image
import pandas as pd

# ###########################################################################
# ########## CORE FUNCTION: _bpm_2610_i4_GET_embedded_album_dynamic_custom ########
# ###########################################################################
def _bpm_2610_i4_GET_embedded_album_dynamic_custom(
    df: pd.DataFrame,
    position: str = "top_left",
    x_offset: int = 10,
    y_offset: int = 10,
    scale: float = 1.0,
    custom_coords: tuple = None
) -> None:
    """
    Overlays each dynamic (donut) PNG image onto its corresponding album JPG image
    and saves the composite by overwriting the original album file (keeping the same file name).
    
    For each row in the DataFrame, the function:
      - Opens the album image from 'Path_jpg_album'.
      - Opens the dynamic overlay image from 'Path_png_bar_dyn'.
      - Optionally rescales the overlay image using the scale factor.
      - Determines placement based on the provided 'position' parameter and separate
        'x_offset' and 'y_offset' values:
          * For "top_left": shifts right by x_offset and downward by y_offset.
          * For "top_right": shifts left by x_offset and downward by y_offset.
          * For "bottom_left": shifts right by x_offset and upward by y_offset.
          * For "bottom_right": shifts left by x_offset and upward by y_offset.
          * For "custom": exact coordinates must be provided in custom_coords.
      - Pastes the overlay onto the album image using its alpha channel.
      - Saves the composite image over the original album JPG (preserving its file name).
    
    Parameters:
        df (pd.DataFrame): DataFrame containing:
            - 'ID': Unique identifier.
            - 'Path_png_bar_dyn': File path to the dynamic overlay PNG image.
            - 'Path_jpg_album': File path to the album JPG image (and destination for the composite).
        position (str): Anchor position for the overlay relative to the album image.
                        Options: "top_left", "top_right", "bottom_left", "bottom_right", "custom".
                        Default is "top_left".
        x_offset (int): Horizontal offset (in pixels) from the anchor position.
                        For "top_left" and "bottom_left", positive values shift the overlay right.
                        For "top_right" and "bottom_right", positive values shift the overlay left.
        y_offset (int): Vertical offset (in pixels) from the anchor position.
                        For "top_left" and "top_right", positive values shift the overlay downward.
                        For "bottom_left" and "bottom_right", positive values shift the overlay upward.
        scale (float): Scaling factor for the overlay image. Default is 1.0 (no scaling).
        custom_coords (tuple): If position is "custom", supply exact (x, y) coordinates.
    """
    for _, row in df.iterrows():
        album_path = row['Path_jpg_album']
        overlay_path = row['Path_png_bar_dyn']
        
        try:
            album_img = Image.open(album_path).convert("RGBA")
            overlay_img = Image.open(overlay_path).convert("RGBA")
        except Exception as e:
            print(f"Error opening images for ID {row['ID']}: {e}")
            continue
        
        # Apply scaling if the scale factor is not 1.0.
        if scale != 1.0:
            new_size = (int(overlay_img.width * scale), int(overlay_img.height * scale))
            overlay_img = overlay_img.resize(new_size, Image.ANTIALIAS)
        
        # Determine placement coordinates based on the selected position.
        if position == "top_left":
            x = x_offset
            y = y_offset
        elif position == "top_right":
            x = album_img.width - overlay_img.width - x_offset
            y = y_offset
        elif position == "bottom_left":
            x = x_offset
            y = album_img.height - overlay_img.height - y_offset
        elif position == "bottom_right":
            x = album_img.width - overlay_img.width - x_offset
            y = album_img.height - overlay_img.height - y_offset
        elif position == "custom":
            if custom_coords is None:
                raise ValueError("Custom coordinates must be provided when position is 'custom'.")
            else:
                x, y = custom_coords
        else:
            raise ValueError("Invalid position value. Choose from: top_left, top_right, bottom_left, bottom_right, custom.")
        
        # Paste the overlay image onto the album image with transparency.
        album_img.paste(overlay_img, (x, y), overlay_img)
        
        # Save the composite over the original album image (converting from RGBA to RGB).
        album_img.convert("RGB").save(album_path, "JPEG")
        print(f"Saved composite over album: {album_path}")
# ########## END OF CORE FUNCTION ###########################################

############### LUFS DONOUTS
# External input: Intervals for LUFS mapping
intervals_lufs_1504 = [
    (-20.00, -19.88, "A"), (-19.88, -19.74, "B"), (-19.74, -19.59, "C"),
    (-19.59, -19.41, "D"), (-19.41, -19.22, "E"), (-19.22, -19.00, "F"),
    (-19.00, -18.76, "G"), (-18.76, -18.49, "H"), (-18.49, -18.18, "I"),
    (-18.18, -17.83, "J"), (-17.83, -17.45, "K"), (-17.45, -17.01, "L"),
    (-17.01, -16.53, "M"), (-16.53, -15.98, "N"), (-15.98, -15.37, "O"),
    (-15.37, -14.68, "P"), (-14.68, -13.91, "Q"), (-13.91, -13.04, "R"),
    (-13.04, -12.07, "S"), (-12.07, -10.98, "T"), (-10.98, -9.76, "U"),
    (-9.76, -8.39, "V"), (-8.39, -6.84, "W"), (-6.84, -5.12, "X"),
    (-5.12, -3.18, "Y"), (-3.18, -1.00, "Z")
]

# 0_FNS
import matplotlib.pyplot as plt
import numpy as np
import os
from tqdm import tqdm

# ###########################################################################
# ########## CORE FUNCTION: _lufs_1504_i1_GET_partialdonut_lufs ###########
# # 
# -----######-----######-----######-----######-----######-----######-----
# 0_FNS
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

# LUFS Color Map (A = darkest, F = brightest)
lufs_color_map = {
    'LuA': '#f90033',  # Light pink red
    'LuB': '#f90033',  # Soft cherry
    'LuC': '#f90033',  # Vibrant rose
    'LuD': '#f90033',  # Deep raspberry
    'LuE': '#f90033',  # Scarlet red
    'LuF': '#f90033',  # Crimson red
}

def _all_values_CREATE_12_LUFS_categories(lufs_value):
    if lufs_value is None:
        return None
    elif lufs_value <= -18:
        return 'LuA'
    elif -18 < lufs_value <= -16:
        return 'LuB'
    elif -16 < lufs_value <= -14:
        return 'LuC'
    elif -14 < lufs_value <= -12:
        return 'LuD'
    elif -12 < lufs_value <= -10:
        return 'Lue'
    else:
        return 'LuF'

# ###########################################################################
# ########## CORE FUNCTION: _lufs_1504_i1_GET_partialdonut_lufs ##########
# ###########################################################################
def _lufs_1504_i1_GET_partialdonut_lufs(df, save_dir="images_lufs"):
    """
    Categorizes LUFS values into A-Z intervals (soft to loud), normalizes to 0–100,
    and generates partial donut plots representing normalized LUFS energy visually.

    Adds columns:
        - 'ms_LUFS_code': A-Z letter
        - 'ms_LUFS_norm': normalized % value
        - 'Path_png_bar_lufs': PNG path to donut image

    Parameters:
        df (pd.DataFrame): Must contain 'ms_lufs' and 'ID' columns
        save_dir (str): Path to store PNG files
    """
    # Map LUFS intervals to A–Z
    intervals = intervals_lufs_1504
    label_lookup = {label: idx for idx, (_, _, label) in enumerate(intervals)}

    os.makedirs(save_dir, exist_ok=True)
    if not save_dir.endswith(os.sep):
        save_dir += os.sep

    lufs_code_list = []
    lufs_norm_list = []
    path_list = []

    print("TQM: Starting LUFS donut generation")

    for _, row in tqdm(df.iterrows(), total=len(df)):
        val = row['ms_lufs']
        code = "NAN"
        for lo, hi, label in intervals:
            if lo <= val < hi:
                code = label
                break
        lufs_code_list.append(code)

        norm_val = (label_lookup.get(code, 0) + 1) / len(intervals) * 100
        lufs_norm_list.append(norm_val)

        # Color category from LUFS value
        lufs_cat = _all_values_CREATE_12_LUFS_categories(val)
        donut_color = lufs_color_map.get(lufs_cat, "#f90033")

        # Donut segments
        segments = [norm_val, 100 - norm_val]
        colors = [donut_color, (0, 0, 0, 0)]  # Main segment and transparent

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.axis('off')
        ax.pie(
            segments,
            colors=colors,
            startangle=90,
            counterclock=False,
            wedgeprops={'width': 0.15, 'edgecolor': 'none'}
        )

        out_path = f"{save_dir}lufs_bar_dyn_{row['ID']}.png"
        plt.savefig(out_path, bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close(fig)
        path_list.append(out_path)

    df['ms_LUFS_code'] = lufs_code_list
    df['ms_LUFS_norm'] = lufs_norm_list
    df['Path_png_bar_lufs'] = path_list

    print("TQM: LUFS donut plots complete!")


###########################################################################
# def _lufs_1504_i1_GET_partialdonut_lufs(df, save_dir="images_lufs"):
#     """
#     Categorizes LUFS values into A-Z intervals (soft to loud), normalizes to 0–100,
#     and generates partial donut plots representing normalized LUFS energy visually.
    
#     Adds columns:
#         - 'ms_LUFS_code': A-Z letter
#         - 'ms_LUFS_norm': normalized % value
#         - 'Path_png_bar_lufs': PNG path to donut image
    
#     Parameters:
#         df (pd.DataFrame): Must contain 'ms_LUFS' and 'ID' columns
#         save_dir (str): Path to store PNG files
#     """
#     # Map LUFS intervals to A–Z
#     intervals = intervals_lufs_1504
#     label_lookup = {label: idx for idx, (_, _, label) in enumerate(intervals)}
    
#     # Make sure save directory exists
#     os.makedirs(save_dir, exist_ok=True)
#     if not save_dir.endswith(os.sep):
#         save_dir += os.sep

#     lufs_code_list = []
#     lufs_norm_list = []
#     path_list = []

#     print("TQM: Starting LUFS donut generation")

#     for _, row in tqdm(df.iterrows(), total=len(df)):
#         val = row['ms_lufs']
#         code = "NAN"
#         for lo, hi, label in intervals:
#             if lo <= val < hi:
#                 code = label
#                 break
#         lufs_code_list.append(code)

#         norm_val = (label_lookup.get(code, 0) + 1) / len(intervals) * 100
#         lufs_norm_list.append(norm_val)

#         # Draw donut
#         segments = [norm_val, 100 - norm_val]
#         colors = ['#FFFFFA', (0, 0, 0, 0)]  # Blue for energy, transparent for rest

#         fig, ax = plt.subplots(figsize=(6, 6))
#         ax.axis('off')
#         ax.pie(
#             segments,
#             colors=colors,
#             startangle=90,
#             counterclock=False,
#             wedgeprops={'width': 0.15, 'edgecolor': 'none'}
#         )

#         out_path = f"{save_dir}lufs_bar_dyn_{row['ID']}.png"
#         plt.savefig(out_path, bbox_inches='tight', pad_inches=0, transparent=True)
#         plt.close(fig)
#         path_list.append(out_path)

#     df['ms_LUFS_code'] = lufs_code_list
#     df['ms_LUFS_norm'] = lufs_norm_list
#     df['Path_png_bar_lufs'] = path_list

#     print("TQM: LUFS donut plots complete!")
# ########## END OF CORE FUNCTION ###########################################

# _lufs_1504_i1_GET_partialdonut_lufs(df, save_dir="images/")
# df['Path_png_bar_lufs'] = f'{direc_jpg}' + 'lufs_bar_dyn_' + df['ID'] + '.png'

# 0_FNS
import os
from PIL import Image
import pandas as pd

# ###########################################################################
# ########## CORE FUNCTION: _lufs_1504_i2_GET_embedded_album_lufs_custom ########
# ###########################################################################
def _lufs_1504_i2_GET_embedded_album_lufs_custom(
    df: pd.DataFrame,
    position: str = "top_left",
    x_offset: int = 10,
    y_offset: int = 10,
    scale: float = 1.0,
    custom_coords: tuple = None
) -> None:
    """
    Embeds LUFS-based donut plots over album covers in-place using coordinates.
    Saves the result over the same JPG path in 'Path_jpg_album'.

    Parameters:
        df (pd.DataFrame): Requires 'Path_jpg_album', 'Path_png_bar_lufs', and 'ID'
        position (str): Anchor placement of donut. Options: top_left, top_right, bottom_left, bottom_right, custom
        x_offset (int): Horizontal offset in pixels
        y_offset (int): Vertical offset in pixels
        scale (float): Optional scale of the donut overlay image (default 1.0)
        custom_coords (tuple): Required if position is "custom" — (x, y) coordinates
    """
    for _, row in df.iterrows():
        album_path = row['Path_jpg_album']
        overlay_path = row['Path_png_bar_lufs']

        try:
            album_img = Image.open(album_path).convert("RGBA")
            overlay_img = Image.open(overlay_path).convert("RGBA")
        except Exception as e:
            print(f"Error opening images for ID {row['ID']}: {e}")
            continue

        if scale != 1.0:
            new_size = (int(overlay_img.width * scale), int(overlay_img.height * scale))
            overlay_img = overlay_img.resize(new_size, Image.ANTIALIAS)

        # Position logic
        if position == "top_left":
            x, y = x_offset, y_offset
        elif position == "top_right":
            x = album_img.width - overlay_img.width - x_offset
            y = y_offset
        elif position == "bottom_left":
            x = x_offset
            y = album_img.height - overlay_img.height - y_offset
        elif position == "bottom_right":
            x = album_img.width - overlay_img.width - x_offset
            y = album_img.height - overlay_img.height - y_offset
        elif position == "custom":
            if custom_coords is None:
                raise ValueError("Custom coordinates required when position is 'custom'")
            x, y = custom_coords
        else:
            raise ValueError(f"Invalid position: {position}")

        album_img.paste(overlay_img, (x, y), overlay_img)
        album_img.convert("RGB").save(album_path, "JPEG")
        print(f"TQM: Embedded LUFS donut for ID {row['ID']} at {album_path}")
# ########## END OF CORE FUNCTION ###########################################





