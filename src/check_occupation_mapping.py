
from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

MATCHES_FILE = OUT / "task_occupation_matches.csv"
PANEL_FILE = OUT / "balanced_task_panel_min100.csv"
DECOMP_FILE = OUT / "gap_change_decomposition.csv"

# ============================================================
# LOAD FILES
# ============================================================

print("=" * 65)
print("O*NET MAPPING QUALITY CHECK")
print("=" * 65)

for path in [MATCHES_FILE, PANEL_FILE, DECOMP_FILE]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

matches = pd.read_csv(MATCHES_FILE)
panel = pd.read_csv(PANEL_FILE)
decomp = pd.read_csv(DECOMP_FILE)

print("\nFiles loaded successfully.")
print(f"Panel rows: {len(panel):,}")
print(f"Mapping rows: {len(matches):,}")
print(f"Decomposition rows: {len(decomp):,}")

# ============================================================
# TASK MATCH STATUS
# ============================================================

task_status = (
    matches.groupby("task", as_index=False)
    .agg(
        occupation_count=("occupation_code", "nunique")
    )
)

task_status["matched"] = task_status["occupation_count"] > 0

total_tasks = len(task_status)
matched_tasks = int(task_status["matched"].sum())
unmatched_tasks = total_tasks - matched_tasks

unique_occupation_tasks = int(
    (task_status["occupation_count"] == 1).sum()
)

multiple_occupation_tasks = int(
    (task_status["occupation_count"] > 1).sum()
)

print("\n" + "=" * 65)
print("MATCH QUALITY")
print("=" * 65)

print(f"Total tasks: {total_tasks}")
print(f"Matched tasks: {matched_tasks}")
print(f"Unmatched tasks: {unmatched_tasks}")
print(f"Tasks with one occupation: {unique_occupation_tasks}")
print(f"Tasks with multiple occupations: {multiple_occupation_tasks}")

# ============================================================
# TASKS PER OCCUPATION
# ============================================================

occupation_counts = (
    matches.dropna(subset=["occupation_code"])
    .groupby(
        ["occupation_code", "occupation_title"],
        as_index=False
    )
    .agg(
        task_count=("task", "nunique")
    )
    .sort_values(
        "task_count",
        ascending=False
    )
)

occupation_counts.to_csv(
    OUT / "occupation_task_counts.csv",
    index=False
)

print("\n" + "=" * 65)
print("OCCUPATION COVERAGE")
print("=" * 65)

print(
    "Occupations with at least 1 task:",
    (occupation_counts["task_count"] >= 1).sum()
)

print(
    "Occupations with at least 3 tasks:",
    (occupation_counts["task_count"] >= 3).sum()
)

print(
    "Occupations with at least 5 tasks:",
    (occupation_counts["task_count"] >= 5).sum()
)

print("\nTOP 10 OCCUPATIONS BY MATCHED TASK COUNT")
print(
    occupation_counts.head(10).to_string(index=False)
)

# ============================================================
# SAVE UNMATCHED TASKS FOR LATER REVIEW
# ============================================================

unmatched = task_status[
    ~task_status["matched"]
].copy()

unmatched.to_csv(
    OUT / "unmatched_task_review.csv",
    index=False
)

print("\n" + "=" * 65)
print("UNMATCHED TASKS")
print("=" * 65)

print(f"Total unmatched tasks: {len(unmatched)}")

print("\nFirst 10 unmatched tasks:")
for task in unmatched["task"].head(10):
    print("-", task)

# ============================================================
# IDENTIFY GAP CHANGE COLUMN
# ============================================================

print("\n" + "=" * 65)
print("GAP-CHANGE ANALYSIS")
print("=" * 65)

print("\nDecomposition columns:")
print(decomp.columns.tolist())

possible_change_columns = [
    "gap_change",
    "gap_change_pp",
    "gap_change_aug_feb"
]

change_col = next(
    (
        col for col in possible_change_columns
        if col in decomp.columns
    ),
    None
)

if change_col is None:
    raise ValueError(
        "Could not identify the gap-change column. "
        "Please send me the printed decomposition columns."
    )

if "task" not in decomp.columns:
    raise ValueError(
        "The decomposition file is missing the task column."
    )

# ============================================================
# COMBINE GAP CHANGES WITH MATCH STATUS
# ============================================================

analysis = decomp.merge(
    task_status,
    on="task",
    how="left",
    validate="one_to_one"
)

if analysis["matched"].isna().any():
    raise ValueError(
        "Some decomposition tasks were not found in the mapping."
    )

# ============================================================
# COMPARE GROUPS
# ============================================================

groups = [
    ("All tasks", analysis),
    ("Matched tasks", analysis[analysis["matched"]]),
    ("Unmatched tasks", analysis[~analysis["matched"]]),
    (
        "Unique-occupation tasks",
        analysis[analysis["occupation_count"] == 1]
    ),
    (
        "Multiple-occupation tasks",
        analysis[analysis["occupation_count"] > 1]
    )
]

summary_rows = []

for label, subset in groups:

    values = pd.to_numeric(
        subset[change_col],
        errors="coerce"
    ).dropna()

    if len(values) == 0:
        continue

    summary_rows.append({
        "group": label,
        "n_tasks": len(values),
        "mean_gap_change_pp": values.mean(),
        "median_gap_change_pp": values.median(),
        "pct_gap_narrowed": 100 * (values < 0).mean(),
        "std_gap_change_pp": values.std()
    })

summary = pd.DataFrame(summary_rows)

print("\nGAP-CHANGE COMPARISON")
print(summary.round(3).to_string(index=False))

# ============================================================
# SAVE RESULTS
# ============================================================

summary.to_csv(
    OUT / "occupation_mapping_quality_summary.csv",
    index=False
)

analysis.to_csv(
    OUT / "gap_change_with_match_status.csv",
    index=False
)

print("\n" + "=" * 65)
print("QUALITY CHECK COMPLETE")
print("=" * 65)

print("\nSaved files:")
print("outputs/occupation_task_counts.csv")
print("outputs/unmatched_task_review.csv")
print("outputs/occupation_mapping_quality_summary.csv")
print("outputs/gap_change_with_match_status.csv")

print(
    "\nThe slow fuzzy-matching process was skipped. "
    "Unmatched tasks were saved for later review."
)
