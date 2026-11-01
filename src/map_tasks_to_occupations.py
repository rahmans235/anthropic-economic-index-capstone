
from pathlib import Path
import re
import unicodedata
import pandas as pd

# ============================================================
# FILE PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

PANEL_FILE = OUTPUT_DIR / "balanced_task_panel_min100.csv"
ONET_FILE = DATA_DIR / "task_statements.csv"

# ============================================================
# NORMALIZE TASK DESCRIPTIONS
# ============================================================

def normalize_task(text):
    if pd.isna(text):
        return ""

    text = unicodedata.normalize("NFKC", str(text))
    text = text.casefold().strip()

    # Normalize curly quotes and dashes
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-")

    # Ignore whitespace differences
    text = re.sub(r"\s+", " ", text)

    # Ignore a final period
    text = text.rstrip(".")

    return text

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 65)
print("O*NET TASK-TO-OCCUPATION MATCHING")
print("=" * 65)

if not PANEL_FILE.exists():
    raise FileNotFoundError(
        f"Missing panel file: {PANEL_FILE}"
    )

if not ONET_FILE.exists():
    raise FileNotFoundError(
        f"Missing O*NET file: {ONET_FILE}"
    )

panel = pd.read_csv(PANEL_FILE)
onet = pd.read_csv(
    ONET_FILE,
    dtype={
        "O*NET-SOC Code": str,
        "Task ID": str
    }
)

print(f"\nPanel rows: {len(panel):,}")
print(f"O*NET task statement rows: {len(onet):,}")

required_panel = {"task"}
required_onet = {
    "O*NET-SOC Code",
    "Title",
    "Task ID",
    "Task"
}

if not required_panel.issubset(panel.columns):
    raise ValueError(
        f"Panel missing columns: "
        f"{required_panel - set(panel.columns)}"
    )

if not required_onet.issubset(onet.columns):
    raise ValueError(
        f"O*NET file missing columns: "
        f"{required_onet - set(onet.columns)}"
    )

# ============================================================
# GET UNIQUE TASKS
# ============================================================

tasks = (
    panel[["task"]]
    .dropna()
    .drop_duplicates()
    .copy()
)

tasks["normalized_task"] = tasks["task"].apply(
    normalize_task
)

onet = onet.rename(
    columns={
        "O*NET-SOC Code": "occupation_code",
        "Title": "occupation_title",
        "Task ID": "onet_task_id",
        "Task": "onet_task_description",
        "Task Type": "task_type"
    }
)

onet["normalized_task"] = (
    onet["onet_task_description"].apply(
        normalize_task
    )
)

# ============================================================
# MATCH TASKS
# ============================================================

mapping_columns = [
    "normalized_task",
    "occupation_code",
    "occupation_title",
    "onet_task_id",
    "onet_task_description"
]

if "task_type" in onet.columns:
    mapping_columns.append("task_type")

mapping = (
    onet[mapping_columns]
    .drop_duplicates()
)

matched = tasks.merge(
    mapping,
    on="normalized_task",
    how="left",
    validate="many_to_many",
    indicator=True
)

matched["matched"] = (
    matched["_merge"] == "both"
)

matched = matched.drop(columns=["_merge"])

# ============================================================
# MATCHING SUMMARY
# ============================================================

task_status = (
    matched.groupby("task", as_index=False)
    .agg(
        matched=("matched", "max"),
        occupation_count=(
            "occupation_code",
            "nunique"
        ),
        onet_task_id_count=(
            "onet_task_id",
            "nunique"
        )
    )
)

total_tasks = len(tasks)

matched_tasks = int(
    task_status["matched"].sum()
)

unmatched_tasks = total_tasks - matched_tasks

multiple_occupations = int(
    (
        task_status["occupation_count"] > 1
    ).sum()
)

match_rate = (
    100 * matched_tasks / total_tasks
    if total_tasks
    else 0
)

print("\n" + "=" * 65)
print("MATCHING SUMMARY")
print("=" * 65)

print(f"\nTotal unique tasks: {total_tasks}")
print(f"Matched tasks: {matched_tasks}")
print(f"Unmatched tasks: {unmatched_tasks}")
print(f"Match rate: {match_rate:.2f}%")

print(
    "Tasks linked to multiple occupations: "
    f"{multiple_occupations}"
)

print(
    "Unique occupations matched: "
    f"{matched['occupation_code'].nunique()}"
)

# ============================================================
# SAVE RESULTS
# ============================================================

matched.to_csv(
    OUTPUT_DIR / "task_occupation_matches.csv",
    index=False
)

task_status.to_csv(
    OUTPUT_DIR / "task_occupation_match_summary.csv",
    index=False
)

unmatched = task_status[
    ~task_status["matched"]
].copy()

unmatched.to_csv(
    OUTPUT_DIR / "unmatched_onet_tasks.csv",
    index=False
)

multi_tasks = task_status[
    task_status["occupation_count"] > 1
].copy()

multi_tasks.to_csv(
    OUTPUT_DIR / "tasks_multiple_occupations.csv",
    index=False
)

# ============================================================
# SHOW EXAMPLES
# ============================================================

print("\nEXAMPLE MATCHED TASKS:")

examples = (
    matched[matched["matched"]]
    [
        [
            "task",
            "occupation_code",
            "occupation_title"
        ]
    ]
    .drop_duplicates()
    .head(10)
)

if not examples.empty:
    print(examples.to_string(index=False))
else:
    print("No exact matches found.")

print("\nEXAMPLE UNMATCHED TASKS:")

if not unmatched.empty:
    print(
        unmatched["task"]
        .head(10)
        .to_string(index=False)
    )
else:
    print("All tasks matched!")

print("\n" + "=" * 65)
print("MATCHING COMPLETE")
print("=" * 65)

print("\nSaved files:")
print("outputs/task_occupation_matches.csv")
print("outputs/task_occupation_match_summary.csv")
print("outputs/unmatched_onet_tasks.csv")
print("outputs/tasks_multiple_occupations.csv")

print(
    "\nNote: These are description-based matches. "
    "They must be checked before occupation-level analysis."
)
