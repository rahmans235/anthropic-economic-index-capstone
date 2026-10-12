
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# --------------------------------------------------
# Find all raw Economic Index CSV files
# --------------------------------------------------

files = sorted(DATA_DIR.glob("aei_raw_*.csv"))

print("=" * 80)
print("ANTHROPIC ECONOMIC INDEX: RELEASE COMPARISON")
print("=" * 80)

print(f"\nNumber of raw CSV files found: {len(files)}")

if not files:
    raise FileNotFoundError(
        "No aei_raw_*.csv files found in the data folder."
    )

# --------------------------------------------------
# Inspect each file
# --------------------------------------------------

summary_rows = []

for file in files:

    print("\n" + "=" * 80)
    print(f"FILE: {file.name}")
    print("=" * 80)

    df = pd.read_csv(file)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nCollection start dates:")
    print(df["date_start"].dropna().unique())

    print("\nCollection end dates:")
    print(df["date_end"].dropna().unique())

    print("\nPlatform labels:")
    print(df["platform_and_product"].dropna().unique())

    # --------------------------------------------------
    # Filter to global collaboration records
    # --------------------------------------------------

    collaboration = df[
        (df["geo_id"] == "GLOBAL")
        & (df["facet"] == "collaboration")
    ].copy()

    print("\nGlobal collaboration records:")
    print(len(collaboration))

    print("\nCollaboration variables:")
    print(
        collaboration["variable"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nCollaboration levels:")
    print(
        collaboration["level"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nCollaboration categories:")
    print(
        collaboration["cluster_name"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nAll global collaboration records:")

    print(
        collaboration[
            [
                "variable",
                "level",
                "cluster_name",
                "value"
            ]
        ].sort_values(
            ["variable", "cluster_name"]
        ).to_string(index=False)
    )

    # --------------------------------------------------
    # Inspect task × collaboration availability
    # --------------------------------------------------

    task_collaboration = df[
        (df["geo_id"] == "GLOBAL")
        & (df["facet"] == "onet_task::collaboration")
    ].copy()

    print("\nTask × collaboration records:")
    print(len(task_collaboration))

    print("\nTask × collaboration variables:")

    print(
        task_collaboration["variable"]
        .value_counts(dropna=False)
        .to_string()
    )

    # --------------------------------------------------
    # Store summary information
    # --------------------------------------------------

    summary_rows.append(
        {
            "file": file.name,
            "rows": len(df),
            "date_start": (
                df["date_start"].dropna().iloc[0]
                if df["date_start"].notna().any()
                else None
            ),
            "date_end": (
                df["date_end"].dropna().iloc[0]
                if df["date_end"].notna().any()
                else None
            ),
            "platform": (
                df["platform_and_product"].dropna().iloc[0]
                if df["platform_and_product"].notna().any()
                else None
            ),
            "global_collaboration_rows": len(collaboration),
            "task_collaboration_rows": len(task_collaboration),
            "collaboration_variables": ", ".join(
                sorted(
                    collaboration["variable"]
                    .dropna()
                    .astype(str)
                    .unique()
                )
            )
        }
    )

# --------------------------------------------------
# Final summary across all files
# --------------------------------------------------

summary = pd.DataFrame(summary_rows)

print("\n" + "=" * 80)
print("SUMMARY ACROSS RELEASES")
print("=" * 80)

print(
    summary.to_string(index=False)
)

print("\n" + "=" * 80)
print("END OF RELEASE INSPECTION")
print("=" * 80)