# -----######-----######-----######-----######-----######
# SAVE DATAFRAME / OBJECT → PKL
# -----######-----######-----######-----######-----######

import pandas as pd

# MODULES -> you want to store in a fn.py and import on the module cell

def _TJ_write_pkl_to_data_folder(df_input, path_save):
    """
    INPUT:
        obj       : any Python object (df, dict, list, model, etc.)
        path_save : full path ending in .pkl

    OUTPUT:
        saves object to disk
    """
    pd.to_pickle(df_input, path_save)
    print('DF is saved to folder name')
    
# -----######-----######-----######-----######-----######
# -----######-----######-----######-----######-----######
# -----######-----######-----######-----######-----######
# LOAD PKL → OBJECT
# -----######-----######-----######-----######-----######

import pandas as pd

def _TJ_import_pkl_w_finance_data(path_load):
    """
    INPUT:
        path_load : full path to .pkl file

    OUTPUT:
        obj       : loaded Python object
    """
    return pd.read_pickle(path_load)