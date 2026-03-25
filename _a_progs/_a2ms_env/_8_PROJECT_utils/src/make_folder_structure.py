
# =========================================================
# -----######-----######  CORE FUNCTION  -----######-----###
# =========================================================

import os
from datetime import datetime
from tqdm import tqdm

def _fld_1803_i1_GET_project_structure(base_dir, project_name):
    """
    Create a structured Ableton project folder.

    Parameters
    ----------
    base_dir : str
        Path where the project folder will be created
    project_name : str
        Name of the project folder

    Returns
    -------
    project_path : str
        Full path of the created project
    """

    # ---------- project root ----------
    project_path = os.path.join(base_dir, project_name)

    # ---------- folder structure ----------
    structure = [
        "_SAMPLES/drums",
        "_SAMPLES/percussion",
        "_SAMPLES/kicks",
        "_SAMPLES/loops",
        "_SAMPLES/synths",
        "_SAMPLES/fx",
        "_SAMPLES/vocals",
        "_RECORDED/resamples",
        "_RECORDED/recordings",
        "_EXPORTS/drafts",
        "_EXPORTS/final",
        "_REFERENCES/tracks",
        "_PRESETS/racks",
        "_PRESETS/fx_chains"
    ]

    # ---------- create root ----------
    os.makedirs(project_path, exist_ok=True)

    # ---------- create folders with TQDM ----------
    for folder in tqdm(structure, desc="Creating project structure"):
        full_path = os.path.join(project_path, folder)
        os.makedirs(full_path, exist_ok=True)

    # ---------- create placeholder ALS file ----------
    als_path = os.path.join(project_path, f"{project_name}.als")
    if not os.path.exists(als_path):
        open(als_path, 'a').close()

    # ---------- return ----------
    print(f"✅ Project created at:{project_path}")
    return project_path
