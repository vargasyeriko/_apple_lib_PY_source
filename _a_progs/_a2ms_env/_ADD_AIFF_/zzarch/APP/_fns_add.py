# -----######-----###### 
# _mix_0804_i1_GET_df_5cols
# -----######-----###### 

import pandas as pd
from tqdm.auto import tqdm

# Enable tqdm progress bar for pandas apply.
tqdm.pandas()

def _mix_0804_i1_GET_df_5cols(df: pd.DataFrame, key_col: str = 'key_dj') -> pd.DataFrame:
    """
    ##### _mix_0804_i1_GET_df_5cols #####
    This function takes a DataFrame with a column containing Camelot keys (e.g., '8A', '12B')
    and appends five new columns based on DJ mixing rules:
    
      - Relative_Key: The key with the same number but with the mode flipped (minor ↔ major).
      - Key_Up: One step forward on the Camelot Wheel (number +1 modulo 12; same mode).
      - Key_Down: One step backward on the Camelot Wheel (number -1 modulo 12; same mode).
      - Jaw_s_Mix: A dissonant key transition, moving -5 steps on the Camelot Wheel (number -5 modulo 12; same mode).
      - Mood_Shifter: A key change that shifts the mood by moving three steps along the Camelot Wheel and flipping the mode.
                      For A keys, move +3 and flip to B.
                      For B keys, move -3 and flip to A.
    
    Parameters:
      df : pd.DataFrame
          DataFrame containing a Camelot key column.
      key_col : str, default 'key_dj'
          Column name in df that contains the Camelot key.
    
    Returns:
      pd.DataFrame:
          The input DataFrame augmented with five new columns:
            'Relative_Key', 'Key_Up', 'Key_Down', 'Jaw_s_Mix', 'Mood_Shifter'
    """
    
    def get_camelot_5_cols(key: str):
        try:
            num = int(key[:-1])
            letter = key[-1].upper()
        except Exception:
            return (None, None, None, None, None)
        
        # Relative_Key: Same number, flip the letter.
        relative = f"{num}{'B' if letter == 'A' else 'A'}"
        
        # Key_Up: One step forward on the number scale.
        up_num = (num % 12) + 1  # if num==12 then up becomes 1.
        key_up = f"{up_num}{letter}"
        
        # Key_Down: One step backward on the number scale.
        down_num = ((num - 2) % 12) + 1  # if num==1 then down becomes 12.
        key_down = f"{down_num}{letter}"
        
        # Jaw_s_Mix: Move -5 steps on the Camelot Wheel.
        jaws_num = (num - 5) % 12
        if jaws_num == 0:
            jaws_num = 12
        jaw_s_mix = f"{jaws_num}{letter}"
        
        # Mood_Shifter:
        # For A keys, move +3 steps and flip mode to B.
        # For B keys, move -3 steps (i.e. opposite direction) and flip mode to A.
        if letter == 'A':
            mood_num = (num + 3) % 12
            if mood_num == 0:
                mood_num = 12
            mood_shifter = f"{mood_num}B"
        else:  # letter == 'B'
            mood_num = (num - 3) % 12
            if mood_num == 0:
                mood_num = 12
            mood_shifter = f"{mood_num}A"
        
        return relative, key_up, key_down, jaw_s_mix, mood_shifter

    # Create new columns using progress_apply with a TQM-style progress bar.
    df[['Relative_Key', 'Key_Up', 'Key_Down', 'Jaw_s_Mix', 'Mood_Shifter']] = df[key_col].progress_apply(
        lambda k: pd.Series(get_camelot_5_cols(k))
    )
    
    return df
