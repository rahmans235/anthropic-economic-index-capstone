from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

api_file = DATA_DIR / "aei_raw_1p_api_2025-08-04_to_2025-08-11.csv"
claude_file = DATA_DIR / "aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv"

api = pd.read_csv(api_file)
claude = pd.read_csv(claude_file)


# --------------------------------------------------
# Inspect task × collaboration structure
# --------------------------------------------------

def inspect_dataset(df, platform_name):

    print("\n" + "=" * 80)
    print(platform_name)
    print("=" * 80)

    # Select global task × collaboration records
    task_collab = df[
        (df["geo_id"].astype(str).str.upper() == "GLOBAL")
        & (df["facet"] == "onet_task::collaboration")
    ].copy()

    print("\nNumber of matching rows:")
    print(len(task_collab))

    print("\nVariables:")
    print(task_collab["variable"].value_counts(dropna=False))

    print("\nLevels:")
    print(task_collab["level"].value_counts(dropna=False))

    print("\nMissing-value rates:")
    print(task_collab.isna().mean())

    print("\nFirst 15 records:")
    print(
        task_collab.head(15).to_string(index=False)
    )

    print("\nSample cluster names:")
    print(
        task_collab["cluster_name"]
        .dropna()
        .drop_duplicates()
        .head(20)
        .to_string(index=False)
    )

    print("\nValue summary by variable:")
    print(
        task_collab.groupby("variable")["value"]
        .agg(["count", "min", "max", "sum"])
        .to_string()
    )

    print("\nExample rows for a software-related task:")

    software_rows = task_collab[
        task_collab["cluster_name"]
        .astype(str)
        .str.contains(
            "modify existing software",
            case=False,
            na=False
        )
    ]

    print(
        software_rows.head(20).to_string(index=False)
    )


# --------------------------------------------------
# Run inspection for both platforms
# --------------------------------------------------

inspect_dataset(api, "FIRST-PARTY API")

inspect_dataset(claude, "CLAUDE.AI")

print("\n" + "=" * 80)
print("END OF TASK × COLLABORATION INSPECTION")
print("=" * 80)