# -----######-----###### MAIN IMPORTS -----######-----######
import os, re
import pandas as pd
from tqdm import tqdm

# ----- helpers -----
def _tqm_print(step, total, label):
    width = 28
    frac = step/float(total) if total else 1.0
    filled = int(width*frac)
    bar = "█"*filled + " "*(width-filled)
    print(f"TQM | {label}: {int(frac*100):3d}%|{bar}| {step}/{total}")

def _sanitize_varname(name):
    # turn "_dfs_STEMS/samples" -> "_dfs_STEMS_samples"
    v = re.sub(r"[^\w]+", "_", name).strip("_")
    if not re.match(r"[A-Za-z_]", v):
        v = "_" + v
    return v

# -----######-----###### CORE IMPORTABLE FUNCTION -----######-----######
def _concat_0810_pkls_GET_df_perfolder(base_dir, assign_globals=True, list_limit=50):
    """
    IN-MEMORY ONLY.
    - Finds subfolders starting with '_dfs'
    - Recursively reads all .pkl per folder, concatenates them
    - Prints a clear, pretty report per folder with PKL names used
    - Prints Missing/Exists if 'Path' column exists
    - Optionally assigns each concat DF into globals() with a sanitized variable name

    Returns: dict { folder_name : concatenated_df }
    """

    # collect target folders
    folder_list = [
        f for f in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, f)) and f.startswith("_dfs")
    ]
    folder_list.sort()

    dfs_dict = {}
    inmem_vars = []

    print("\n══════════════════════════════════════════════════════════════════")
    print(f"📁 BASE: {base_dir}")
    print(f"📦 Detected '_dfs*' folders: {len(folder_list)}")
    print("══════════════════════════════════════════════════════════════════")

    for i, folder in enumerate(folder_list, 1):
        folder_path = os.path.join(base_dir, folder)

        # gather .pkl files
        pkl_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".pkl"):
                    pkl_files.append(os.path.join(root, file))
        pkl_files.sort()

        # read and concat
        dfs = []
        for pkl in tqdm(pkl_files, desc=f"🔍 {folder}", leave=False):
            try:
                df = pd.read_pickle(pkl)
                dfs.append(df)
            except Exception as e:
                print(f"⚠️ Error reading {pkl}: {e}")

        # pretty per-folder block
        print("\n──────────────────────────────────────────────────────────────────")
        print(f"📂 FOLDER: {folder}")
        if pkl_files:
            basenames = [os.path.basename(p) for p in pkl_files]
            show = basenames[:list_limit]
            more = len(basenames) - len(show)
            print(f"   • PKLs found: {len(basenames)}")
            print(f"   • Used in concat:")
            for nm in show:
                print(f"     - {nm}")
            if more > 0:
                print(f"     … (+{more} more)")
        else:
            print("   • PKLs found: 0")
            print("   • Used in concat: —")

        if dfs:
            df_concat = pd.concat(dfs, ignore_index=True)
            dfs_dict[folder] = df_concat

            total = len(df_concat)
            if "Path" in df_concat.columns:
                missing = df_concat["Path"].apply(
                    lambda x: not os.path.exists(x) if pd.notna(x) else True
                ).sum()
                exists = total - missing
                print(f"   • Rows: {total:,}")
                print(f"   • Paths  →  ❌ Missing: {missing:,} / {total:,}   ✅ Exists: {exists:,}")
            else:
                print(f"   • Rows: {total:,} (no 'Path' column)")

            if assign_globals:
                var_name = _sanitize_varname(folder)
                globals()[var_name] = df_concat
                inmem_vars.append((var_name, total))
                print(f"   • In-memory DF variable: {var_name}  (rows: {total:,})")
        else:
            print("   • Concat: ⚠️ No dataframes read → 0 rows")

        _tqm_print(i, len(folder_list), "Folder Progress")

    # final memory summary
    print("\n══════════════════════════════════════════════════════════════════")
    print("📚 CONCAT DFS CURRENTLY IN THIS NOTEBOOK SESSION (in-memory)")
    if inmem_vars:
        for nm, nrows in inmem_vars:
            print(f"   → {nm:<32} (rows: {nrows:,})")
    else:
        print("   → None")
    print("══════════════════════════════════════════════════════════════════\n")

    return dfs_dict
