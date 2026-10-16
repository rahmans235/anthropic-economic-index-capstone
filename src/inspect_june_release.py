from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# --------------------------------------------------
# June 2026 files
# --------------------------------------------------

FILES = [
    DATA_DIR / "aei_1p_api_2026-06-26.csv",
    DATA_DIR / "aei_claude_ai_2026-06-26.csv",
]

print("=" * 80)
print("JUNE 2026 RELEASE INSPECTION")
print("=" * 80)

# --------------------------------------------------
# Inspect each file
# --------------------------------------------------

for file_path in FILES:

    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    if not file_path.exists():
        print("FILE NOT FOUND")
        print(f"Expected location: {file_path}")
        continue

    # low_memory=False avoids mixed-type warnings
    df = pd.read_csv(file_path, low_memory=False)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nCOLUMN NAMES:")
    print(df.columns.tolist())

    # --------------------------------------------------
    # Data types
    # --------------------------------------------------

    print("\nDATA TYPES:")
    print(df.dtypes.to_string())

    # --------------------------------------------------
    # First few rows
    # --------------------------------------------------

    print("\nFIRST 5 ROWS:")
    print(df.head().to_string(index=False))

    # --------------------------------------------------
    # Missing values
    # --------------------------------------------------

    print("\nMISSING VALUES:")
    missing = df.isna().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values.")
    else:
        print(missing.to_string())

    # --------------------------------------------------
    # Date-related columns
    # --------------------------------------------------

    print("\nDATE-RELATED COLUMNS:")

    date_columns = [
        col for col in df.columns
        if "date" in col.lower()
        or "month" in col.lower()
        or "period" in col.lower()
    ]

    print(date_columns)

    for col in date_columns:

        print(f"\nUnique values for {col}:")

        values = df[col].dropna().unique()

        print(values[:30])

        if len(values) > 30:
            print(
                f"... {len(values):,} unique values total"
            )

    # --------------------------------------------------
    # Platform/product-related columns
    # --------------------------------------------------

    print("\nPLATFORM/PRODUCT-RELATED COLUMNS:")

    platform_columns = [
        col for col in df.columns
        if "platform" in col.lower()
        or "product" in col.lower()
    ]

    print(platform_columns)

    for col in platform_columns:

        print(f"\nValue counts for {col}:")

        print(
            df[col]
            .value_counts(dropna=False)
            .head(30)
            .to_string()
        )

    # --------------------------------------------------
    # Category / hierarchy information
    # --------------------------------------------------

    possible_category_columns = [
        "category_name",
        "hierarchy_level",
        "metric_id",
        "node_name",
    ]

    print("\nCATEGORY / HIERARCHY INFORMATION:")

    for col in possible_category_columns:

        if col in df.columns:

            print(f"\n{col}:")

            print(
                df[col]
                .value_counts(dropna=False)
                .head(40)
                .to_string()
            )

    # --------------------------------------------------
    # Search column names for concepts we care about
    # --------------------------------------------------

    print("\nRELEVANT COLUMN NAMES:")

    keywords = [
        "collab",
        "automat",
        "task",
        "onet",
        "count",
        "pct",
        "percent",
    ]

    relevant_columns = [
        col for col in df.columns
        if any(
            keyword in col.lower()
            for keyword in keywords
        )
    ]

    print(relevant_columns)

    # --------------------------------------------------
    # Search metric IDs
    # --------------------------------------------------

    if "metric_id" in df.columns:

        metric_text = df["metric_id"].astype(str)

        relevant_metrics = sorted(
            df.loc[
                metric_text.str.contains(
                    "collab|automat|task|onet",
                    case=False,
                    na=False,
                    regex=True,
                ),
                "metric_id",
            ]
            .dropna()
            .astype(str)
            .unique()
        )

        print("\nRELEVANT METRIC IDs:")

        for metric in relevant_metrics:
            print(metric)

        print(
            f"\nNumber of relevant metric IDs: "
            f"{len(relevant_metrics):,}"
        )

    # --------------------------------------------------
    # Search node names
    # --------------------------------------------------

    if "node_name" in df.columns:

        node_text = df["node_name"].astype(str)

        automation_nodes = sorted(
            df.loc[
                node_text.str.contains(
                    "directive|feedback loop|automation|"
                    "task iteration|learning|validation",
                    case=False,
                    na=False,
                    regex=True,
                ),
                "node_name",
            ]
            .dropna()
            .astype(str)
            .unique()
        )

        print("\nAUTOMATION/COLLABORATION NODE NAMES:")

        for node in automation_nodes[:100]:
            print(node)

        print(
            f"\nNumber of matching node names: "
            f"{len(automation_nodes):,}"
        )

    # --------------------------------------------------
    # Inspect rows containing automation/collaboration
    # --------------------------------------------------

    search_columns = [
        col for col in [
            "category_name",
            "metric_id",
            "node_name",
        ]
        if col in df.columns
    ]

    if search_columns:

        mask = pd.Series(False, index=df.index)

        for col in search_columns:

            mask = mask | (
                df[col]
                .astype(str)
                .str.contains(
                    "collab|automat",
                    case=False,
                    na=False,
                    regex=True,
                )
            )

        relevant_rows = df[mask].copy()

        print("\nROWS RELATED TO COLLABORATION/AUTOMATION:")
        print(f"Number of matching rows: {len(relevant_rows):,}")

        if len(relevant_rows) > 0:

            display_columns = [
                col for col in [
                    "date",
                    "month",
                    "period",
                    "platform_and_product",
                    "product",
                    "category_name",
                    "hierarchy_level",
                    "metric_id",
                    "node_name",
                    "value",
                ]
                if col in relevant_rows.columns
            ]

            print(
                relevant_rows[
                    display_columns
                ]
                .head(100)
                .to_string(index=False)
            )

print("\n" + "=" * 80)
print("END OF JUNE 2026 INSPECTION")
print("=" * 80)