
from pathlib import Path
import pandas as pd

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"

# ============================================================
# LOAD OUR MATCHED TASKS
# ============================================================

panel_path = OUTPUT_DIR / "balanced_task_panel_min100.csv"

panel = pd.read_csv(panel_path)
matched_tasks = set(panel["task"].dropna().unique())

print("=" * 70)
print("OCCUPATION MAPPING INSPECTION")
print("=" * 70)

print(f"\nMatched tasks in main analysis: {len(matched_tasks)}")

# ============================================================
# FIND ALL CSV FILES
# ============================================================

csv_files = sorted(DATA_DIR.glob("*.csv"))

print(f"\nCSV files found: {len(csv_files)}")

if not csv_files:
    raise FileNotFoundError(
        "No CSV files found in the data folder."
    )

# ============================================================
# INSPECT EACH FILE
# ============================================================

for path in csv_files:

    print("\n" + "=" * 70)
    print(f"FILE: {path.name}")
    print("=" * 70)

    try:
        # Read a small sample to identify the file format
        sample = pd.read_csv(
            path,
            nrows=1000,
            engine="python"
        )

        print("\nColumns:")
        print(sample.columns.tolist())

        # ====================================================
        # OLD RELEASE FORMAT
        # ====================================================

        if "facet" in sample.columns:

            print("\nOLD RELEASE FORMAT")

            # Read only needed columns in chunks.
            # This avoids loading the entire file into memory.

            facet_counts = pd.Series(dtype="int64")
            level_counts = pd.Series(dtype="int64")
            occupation_fields = []

            for chunk in pd.read_csv(
                path,
                usecols=[
                    "facet",
                    "level",
                    "variable",
                    "cluster_name"
                ],
                chunksize=50000,
                engine="python"
            ):

                facet_counts = facet_counts.add(
                    chunk["facet"].value_counts(),
                    fill_value=0
                )

                level_counts = level_counts.add(
                    chunk["level"].value_counts(),
                    fill_value=0
                )

                mask = (
                    chunk["facet"]
                    .astype(str)
                    .str.contains(
                        "occupation|soc|onet",
                        case=False,
                        regex=True
                    )
                )

                relevant = (
                    chunk.loc[
                        mask,
                        ["facet", "level", "variable"]
                    ]
                    .drop_duplicates()
                )

                if not relevant.empty:
                    occupation_fields.append(relevant)

            print("\nFacets:")
            print(
                facet_counts
                .sort_values(ascending=False)
                .astype(int)
                .to_string()
            )

            print("\nLevels:")
            print(
                level_counts
                .sort_index()
                .astype(int)
                .to_string()
            )

            print("\nOccupation-related fields:")

            if occupation_fields:

                fields = (
                    pd.concat(
                        occupation_fields,
                        ignore_index=True
                    )
                    .drop_duplicates()
                )

                print(
                    fields
                    .head(30)
                    .to_string(index=False)
                )

            else:
                print("No occupation-related fields found.")

        # ====================================================
        # NEW RELEASE FORMAT
        # ====================================================

        elif "category_name" in sample.columns:

            print("\nNEW RELEASE FORMAT")

            category_counts = pd.Series(dtype="int64")
            occupation_examples = []

            for chunk in pd.read_csv(
                path,
                chunksize=100000,
                engine="python"
            ):

                category_counts = category_counts.add(
                    chunk["category_name"].value_counts(),
                    fill_value=0
                )

                occupation_rows = chunk[
                    chunk["category_name"]
                    .astype(str)
                    .str.contains(
                        "occupation|soc",
                        case=False,
                        regex=True
                    )
                ]

                if (
                    len(occupation_examples) < 5
                    and not occupation_rows.empty
                ):

                    occupation_examples.append(
                        occupation_rows[
                            [
                                "category_name",
                                "hierarchy_level",
                                "metric_id",
                                "node_name",
                                "node_external_id"
                            ]
                        ].head(5)
                    )

            print("\nCategories:")
            print(
                category_counts
                .sort_values(ascending=False)
                .astype(int)
                .to_string()
            )

            print("\nOccupation examples:")

            if occupation_examples:

                print(
                    pd.concat(
                        occupation_examples,
                        ignore_index=True
                    )
                    .head(10)
                    .to_string(index=False)
                )

            else:
                print("No occupation examples found.")

        else:
            print(
                "\nUnknown CSV format. "
                "Skipping this file."
            )

    except Exception as error:

        print("\nWARNING: Could not inspect this file.")
        print(f"Error type: {type(error).__name__}")
        print(f"Details: {error}")

        print("Continuing to the next file...")

# ============================================================
# FINISH
# ============================================================

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)

print(
    "\nNext step: determine whether the historical "
    "O*NET tasks can be reliably mapped to occupations."
)

