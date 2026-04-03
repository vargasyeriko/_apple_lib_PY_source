
# ---------------------------------------------------
# DATA LOADER MODULE
# ---------------------------------------------------

import pandas as pd
from pathlib import Path


def load_dataset(path, save_processed=False, processed_dir="data/processed"):
    """
    Load dataset from CSV or PKL.

    Parameters
    ----------
    path : str
        Path to dataset

    save_processed : bool
        If True, saves a PKL version in processed folder

    processed_dir : str
        Directory where processed files are stored

    Returns
    -------
    df : pandas.DataFrame
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()

    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------

    if ext == ".csv":
        df = pd.read_csv(path)

    elif ext == ".pkl":
        df = pd.read_pickle(path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # ---------------------------------------------------
    # BASIC DATA INFO
    # ---------------------------------------------------

    print("\nDataset Loaded")
    print("---------------------------")
    print(f"File: {path.name}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    mem = df.memory_usage(deep=True).sum() / 1024**2
    print(f"Memory usage: {mem:.2f} MB")

    # ---------------------------------------------------
    # OPTIONAL SAVE PROCESSED
    # ---------------------------------------------------

    if save_processed:

        processed_dir = Path(processed_dir)
        processed_dir.mkdir(parents=True, exist_ok=True)

        new_file = processed_dir / f"{path.stem}.pkl"

        df.to_pickle(new_file)

        print(f"Saved processed dataset -> {new_file}")

    return df
