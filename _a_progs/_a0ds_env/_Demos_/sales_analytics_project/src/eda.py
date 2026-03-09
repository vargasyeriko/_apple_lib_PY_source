
# ---------------------------------------------------------
# SIMPLE EDA (STEPS 1–6) + REPORT EXPORT
# does NOT modify df
# ---------------------------------------------------------

import pandas as pd
from pathlib import Path

def eda_01_06_GET_report(df, path_out="reports/tables/eda_summary.csv"):

    # ------------------------------------------------
    # Console overview
    # ------------------------------------------------
    print("\nDATA SHAPE:", df.shape)
    print("\nCOLUMNS:", list(df.columns))

    print("\nHEAD:\n", df.head())
    print("\nTAIL:\n", df.tail())

    print("\nDATA INFO:")
    df.info()

    print("\nDUPLICATE ROWS:", df.duplicated().sum())

    # ------------------------------------------------
    # Target overview
    # ------------------------------------------------
    if "purchase" in df.columns:
        print("\nTARGET DISTRIBUTION:")
        print(df["purchase"].value_counts())

    # ------------------------------------------------
    # Report table
    # ------------------------------------------------
    report = pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.values,
        "missing": df.isna().sum().values,
        "missing_%": (df.isna().mean()*100).round(2).values,
        "unique": df.nunique().values
    })

    # ------------------------------------------------
    # Save report
    # ------------------------------------------------
    Path(path_out).parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(path_out, index=False)

    print("\nREPORT SAVED →", path_out)

    return report
