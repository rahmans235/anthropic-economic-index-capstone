from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Find all CSV files in the data folder
csv_files = sorted(DATA_DIR.glob("*.csv"))

print("=" * 70)
print("DATASET INVENTORY")
print("=" * 70)

# --------------------------------------------------
# Loop through each CSV file
# --------------------------------------------------

for file_path in csv_files:

    print(f"\nFILE: {file_path.name}")

    # --------------------------------------------------
    # File size
    # --------------------------------------------------

    size_mb = file_path.stat().st_size / (1024 ** 2)
    print(f"File size: {size_mb:.2f} MB")

    # --------------------------------------------------
    # Read data
    # --------------------------------------------------

    df = pd.read_csv(file_path)

    # --------------------------------------------------
    # Row and column counts
    # --------------------------------------------------

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # --------------------------------------------------
    # Column names and data types
    # --------------------------------------------------

    print("\nColumns and data types:")
    print(df.dtypes)

    # --------------------------------------------------
    # Missing-value rates
    # --------------------------------------------------

    print("\nMissing-value rates:")
    missing_rates = df.isna().mean().sort_values(ascending=False)
    print(missing_rates)

    print("-" * 70)

    # --------------------------------------------------
    # Platform/product values
    # --------------------------------------------------

    print("\nUnique platform/product values:")
    print(df["platform_and_product"].unique())

    # --------------------------------------------------
    # Facets
    # --------------------------------------------------

    print("\nUnique facets:")
    print(df["facet"].unique())

    # --------------------------------------------------
    # Levels
    # --------------------------------------------------

    print("\nUnique levels:")
    print(sorted(df["level"].unique()))

    # --------------------------------------------------
    # Variables
    # --------------------------------------------------

    print("\nSample variable values:")
    print(df["variable"].dropna().unique()[:30])

    # --------------------------------------------------
    # Collaboration categories
    # --------------------------------------------------

    collaboration = df[
        (df["facet"] == "collaboration")
        & (df["variable"] == "collaboration_pct")
    ]

    print("\nUnique collaboration categories:")
    print(collaboration["cluster_name"].dropna().unique())

    # --------------------------------------------------
    # Inspect level 0 collaboration structure
    # --------------------------------------------------

    level0_collab = df[
        (df["facet"] == "collaboration")
        & (df["variable"] == "collaboration_pct")
        & (df["level"] == 0)
    ]

    print("\nLevel 0 collaboration_pct structure:")

    print(f"Number of rows: {len(level0_collab)}")

    print(
        f"Unique geo_id values: "
        f"{level0_collab['geo_id'].nunique(dropna=False)}"
    )

    print(
        f"Unique geography values: "
        f"{level0_collab['geography'].nunique(dropna=False)}"
    )

    print("\nSample rows:")

    print(
        level0_collab[
            [
                "geo_id",
                "geography",
                "level",
                "cluster_name",
                "value",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    # --------------------------------------------------
    # Look for true global collaboration rows
    # --------------------------------------------------

    print("\nGlobal collaboration_pct rows:")

    global_collab = df[
        (df["facet"] == "collaboration")
        & (df["variable"] == "collaboration_pct")
        & (
            (df["geo_id"].astype(str).str.upper() == "GLOBAL")
            | (df["geography"].astype(str).str.lower() == "global")
        )
    ]

    print(f"Number of global rows: {len(global_collab)}")

    if len(global_collab) > 0:
        print(
            global_collab[
                [
                    "geo_id",
                    "geography",
                    "level",
                    "cluster_name",
                    "value",
                ]
            ].to_string(index=False)
        )
    else:
        print("No global collaboration_pct rows found.")

    # --------------------------------------------------
    # Automation and augmentation categories
    # --------------------------------------------------

    automation_categories = [
        "directive",
        "feedback loop",
    ]

    augmentation_categories = [
        "learning",
        "task iteration",
        "validation",
    ]
        # --------------------------------------------------
    # Verification: largest API O*NET task categories
    # --------------------------------------------------

    if "1P API" in df["platform_and_product"].unique():

        print("\nTop API O*NET task records:")

        api_tasks = df[
            (df["facet"] == "onet_task")
            & (df["variable"] == "onet_task_pct")
            & (df["geo_id"].astype(str).str.upper() == "GLOBAL")
        ].copy()

        print(f"Number of matching task rows: {len(api_tasks)}")

        print(
            api_tasks[
                [
                    "level",
                    "cluster_name",
                    "value",
                ]
            ]
            .sort_values("value", ascending=False)
            .head(20)
            .to_string(index=False)
        )

    # --------------------------------------------------
    # Calculate automation/augmentation only if
    # true global collaboration rows are available
    # --------------------------------------------------

    if len(global_collab) > 0:

        automation = global_collab[
            global_collab["cluster_name"].isin(
                automation_categories
            )
        ]["value"].sum()

        augmentation = global_collab[
            global_collab["cluster_name"].isin(
                augmentation_categories
            )
        ]["value"].sum()

        print("\nGlobal collaboration classification:")
        print(f"Automation: {automation:.2f}%")
        print(f"Augmentation: {augmentation:.2f}%")

    else:

        print("\nGlobal collaboration classification:")
        print(
            "Cannot calculate from collaboration_pct because "
            "no global rows were found."
        )

    print("\n" + "=" * 70)