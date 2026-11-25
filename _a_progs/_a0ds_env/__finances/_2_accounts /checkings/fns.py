# ============================== 0_FNS ==============================

from pathlib import Path
from typing import Union

import pandas as pd
from tqdm.auto import tqdm


# -----######-----###### CORE IMPORTABLE FUNCTION -----######-----######
def _xlsx_1607_i3_GET_all_accounts(
    data_folder: Union[str, Path],
    file_template: str = "finances_{year}.xlsx",
    start_year: int = 2021,
    end_year: int = 2026,
    output_filename: str = "finances_2021_2026.xlsx",
    output_sheet: str = "ALL_TRANSACTIONS",
) -> pd.DataFrame:
    """
    Read every sheet from every yearly workbook.

    Skips only:
    - Summaries
    - Previously generated ALL_TRANSACTIONS sheets

    All account sheets, including newly added accounts, are included.
    Columns are aligned by column name.
    """

    data_folder = Path(data_folder).expanduser().resolve()
    output_path = data_folder / output_filename

    all_frames: list[pd.DataFrame] = []
    processing_log: list[dict] = []

    yearly_files = [
        data_folder / file_template.format(year=year)
        for year in range(start_year, end_year + 1)
    ]

    for file_path in tqdm(
        yearly_files,
        desc="Processing yearly workbooks",
        unit="workbook",
    ):
        if not file_path.exists():
            print(f"MISSING: {file_path.name}")
            continue

        excel_file = pd.ExcelFile(
            file_path,
            engine="openpyxl",
        )

        # Every real account sheet is included.
        sheets_to_read = [
            sheet_name
            for sheet_name in excel_file.sheet_names
            if sheet_name.strip().lower()
            not in {
                "summaries",
                output_sheet.strip().lower(),
            }
        ]

        print(f"\n{file_path.name}")
        print(f"Account sheets found: {sheets_to_read}")

        for sheet_name in tqdm(
            sheets_to_read,
            desc=f"Reading {file_path.name}",
            unit="sheet",
            leave=False,
        ):
            df_sheet = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                engine="openpyxl",
            )

            # Remove fully empty rows and columns.
            df_sheet = (
                df_sheet
                .dropna(axis=0, how="all")
                .dropna(axis=1, how="all")
            )

            if df_sheet.empty:
                print(f"EMPTY SHEET: {sheet_name}")
                continue

            # Standardize column headers.
            df_sheet.columns = [
                str(column).strip()
                for column in df_sheet.columns
            ]

            # Stop if one sheet contains duplicate column names.
            duplicate_columns = (
                df_sheet.columns[
                    df_sheet.columns.duplicated()
                ]
                .tolist()
            )

            if duplicate_columns:
                raise ValueError(
                    f"Duplicate columns found in "
                    f"{file_path.name} / {sheet_name}: "
                    f"{duplicate_columns}"
                )

            # Trace every row back to its original location.
            df_sheet["source_year"] = file_path.stem.split("_")[-1]
            df_sheet["source_file"] = file_path.name
            df_sheet["source_sheet"] = sheet_name

            all_frames.append(df_sheet)

            processing_log.append(
                {
                    "file": file_path.name,
                    "sheet": sheet_name,
                    "rows": len(df_sheet),
                    "columns": len(df_sheet.columns),
                }
            )

            print(
                f"ADDED: {sheet_name} | "
                f"{len(df_sheet):,} rows"
            )

    if not all_frames:
        raise ValueError(
            f"No account data found inside: {data_folder}"
        )

    # Column names are matched automatically.
    # New account-specific columns are preserved.
    df_all = pd.concat(
        all_frames,
        axis=0,
        ignore_index=True,
        sort=False,
    )

    # Exactly one output workbook with exactly one sheet.
    with pd.ExcelWriter(
        output_path,
        engine="openpyxl",
        mode="w",
    ) as writer:
        df_all.to_excel(
            writer,
            sheet_name=output_sheet,
            index=False,
        )

        worksheet = writer.book[output_sheet]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

    print("\n================ COMPLETE ================")
    print(f"Account sheets combined: {len(processing_log):,}")
    print(f"Total rows: {len(df_all):,}")
    print(f"Total columns: {len(df_all.columns):,}")
    print(f"Output sheet count: 1")
    print(f"Saved to: {output_path}")

    return df_all