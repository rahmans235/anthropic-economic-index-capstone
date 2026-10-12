from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# Files and period labels
# --------------------------------------------------

FILES = [
    (
        "Aug 2025",
        "API",
        DATA_DIR / "aei_raw_1p_api_2025-08-04_to_2025-08-11.csv",
    ),
    (
        "Aug 2025",
        "Claude.ai",
        DATA_DIR / "aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv",
    ),
    (
        "Nov 2025",
        "API",
        DATA_DIR / "aei_raw_1p_api_2025-11-13_to_2025-11-20.csv",
    ),
    (
        "Nov 2025",
        "Claude.ai",
        DATA_DIR / "aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
    ),
    (
        "Feb 2026",
        "API",
        DATA_DIR / "aei_raw_1p_api_2026-02-05_to_2026-02-12.csv",
    ),
    (
        "Feb 2026",
        "Claude.ai",
        DATA_DIR / "aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv",
    ),
]

AUTOMATION = ["directive", "feedback loop"]

# Preliminary screening threshold
MIN_COUNT = 100


# --------------------------------------------------
# Function to process one file
# --------------------------------------------------

def process_file(period, platform, file_path):

    print(f"\nReading: {file_path.name}")

    # low_memory=False avoids the mixed-type warning
    df = pd.read_csv(file_path, low_memory=False)

    # Keep global task × collaboration counts
    tasks = df[
        (df["geo_id"] == "GLOBAL")
        & (df["facet"] == "onet_task::collaboration")
        & (df["variable"] == "onet_task_collaboration_count")
    ].copy()

    # Make sure cluster_name is treated as text
    tasks["cluster_name"] = tasks["cluster_name"].astype(str)

    # Split:
    # O*NET task description::collaboration style
    split = tasks["cluster_name"].str.rsplit(
        "::",
        n=1,
        expand=True
    )

    tasks["task"] = split[0].str.strip()
    tasks["collaboration"] = split[1].str.strip()

    # Remove rows where the O*NET task itself is unclassified
    tasks = tasks[
        ~tasks["task"].isin(["none", "not_classified"])
    ].copy()

    # Mark automation observations
    tasks["automation_count"] = tasks["value"].where(
        tasks["collaboration"].isin(AUTOMATION),
        0
    )

    # --------------------------------------------------
    # Collapse collaboration styles to one row per task
    # --------------------------------------------------

    task_summary = (
        tasks
        .groupby("task", as_index=False)
        .agg(
            total_count=("value", "sum"),
            automation_count=("automation_count", "sum")
        )
    )

    task_summary["automation_pct"] = (
        100
        * task_summary["automation_count"]
        / task_summary["total_count"]
    )

    task_summary["period"] = period
    task_summary["platform"] = platform

    print(f"Unique classified tasks: {len(task_summary):,}")

    return task_summary


# --------------------------------------------------
# Process all six files
# --------------------------------------------------

frames = []

for period, platform, file_path in FILES:
    frames.append(
        process_file(period, platform, file_path)
    )

panel = pd.concat(frames, ignore_index=True)

print("\n" + "=" * 80)
print("FULL TASK PANEL")
print("=" * 80)

print(f"Rows in full panel: {len(panel):,}")
print(f"Unique tasks overall: {panel['task'].nunique():,}")


# --------------------------------------------------
# Determine task coverage
# --------------------------------------------------

coverage = (
    panel
    .groupby("task")
    .agg(
        observations=("task", "size"),
        periods=("period", "nunique"),
        platforms=("platform", "nunique"),
        minimum_count=("total_count", "min")
    )
    .reset_index()
)

# A fully matched task must appear:
# 3 periods × 2 platforms = 6 observations
fully_matched_tasks = coverage[
    (coverage["observations"] == 6)
    & (coverage["periods"] == 3)
    & (coverage["platforms"] == 2)
].copy()

print("\n" + "=" * 80)
print("TASK COVERAGE")
print("=" * 80)

print(
    f"Tasks present on both platforms in all 3 periods: "
    f"{len(fully_matched_tasks):,}"
)

# --------------------------------------------------
# Apply preliminary minimum-count rule
# --------------------------------------------------

eligible_tasks = fully_matched_tasks[
    fully_matched_tasks["minimum_count"] >= MIN_COUNT
].copy()

print(
    f"Tasks with >= {MIN_COUNT} observations in "
    f"EVERY platform-period combination: "
    f"{len(eligible_tasks):,}"
)

# --------------------------------------------------
# Create balanced panel
# --------------------------------------------------

balanced_panel = panel[
    panel["task"].isin(eligible_tasks["task"])
].copy()

period_order = {
    "Aug 2025": 1,
    "Nov 2025": 2,
    "Feb 2026": 3,
}

balanced_panel["period_order"] = (
    balanced_panel["period"].map(period_order)
)

balanced_panel = balanced_panel.sort_values(
    ["task", "period_order", "platform"]
)

print("\nBalanced panel rows:", len(balanced_panel))

expected_rows = len(eligible_tasks) * 6

print("Expected rows:", expected_rows)

if len(balanced_panel) == expected_rows:
    print("CHECK PASSED: balanced panel has the expected number of rows.")
else:
    print("WARNING: balanced panel does not have the expected number of rows.")


# --------------------------------------------------
# Platform averages by period
#
# These are UNWEIGHTED task-level means.
# They are NOT the same as the overall global
# collaboration percentages.
# --------------------------------------------------

period_summary = (
    balanced_panel
    .groupby(["period_order", "period", "platform"])
    .agg(
        tasks=("task", "nunique"),
        mean_task_automation_pct=("automation_pct", "mean"),
        median_task_automation_pct=("automation_pct", "median"),
        total_task_count=("total_count", "sum")
    )
    .reset_index()
    .sort_values(["period_order", "platform"])
)

print("\n" + "=" * 80)
print("BALANCED-PANEL SUMMARY")
print("=" * 80)

print(period_summary.to_string(index=False))


# --------------------------------------------------
# Calculate within-task API - Claude.ai gaps
# --------------------------------------------------

wide = balanced_panel.pivot(
    index=["task", "period_order", "period"],
    columns="platform",
    values="automation_pct"
).reset_index()

wide["gap_pp"] = wide["API"] - wide["Claude.ai"]

gap_summary = (
    wide
    .groupby(["period_order", "period"])
    .agg(
        tasks=("task", "nunique"),
        mean_gap_pp=("gap_pp", "mean"),
        median_gap_pp=("gap_pp", "median"),
        min_gap_pp=("gap_pp", "min"),
        max_gap_pp=("gap_pp", "max")
    )
    .reset_index()
    .sort_values("period_order")
)

print("\n" + "=" * 80)
print("WITHIN-TASK API - CLAUDE.AI AUTOMATION GAPS")
print("=" * 80)

print(gap_summary.to_string(index=False))


# --------------------------------------------------
# Direction of the gap
# --------------------------------------------------

direction = (
    wide
    .assign(
        direction=lambda x:
        x["gap_pp"].apply(
            lambda value:
            "API higher"
            if value > 0
            else (
                "Claude.ai higher"
                if value < 0
                else "Equal"
            )
        )
    )
    .groupby(["period_order", "period", "direction"])
    .size()
    .reset_index(name="tasks")
    .sort_values(["period_order", "direction"])
)

print("\n" + "=" * 80)
print("DIRECTION OF TASK-LEVEL GAP")
print("=" * 80)

print(direction.to_string(index=False))


# --------------------------------------------------
# Save outputs
# --------------------------------------------------

panel.to_csv(
    OUTPUT_DIR / "task_panel_all.csv",
    index=False
)

fully_matched_tasks.to_csv(
    OUTPUT_DIR / "tasks_all_three_periods.csv",
    index=False
)

eligible_tasks.to_csv(
    OUTPUT_DIR / "tasks_all_three_periods_min100.csv",
    index=False
)

balanced_panel.to_csv(
    OUTPUT_DIR / "balanced_task_panel_min100.csv",
    index=False
)

period_summary.to_csv(
    OUTPUT_DIR / "balanced_panel_period_summary.csv",
    index=False
)

gap_summary.to_csv(
    OUTPUT_DIR / "balanced_panel_gap_summary.csv",
    index=False
)

wide.to_csv(
    OUTPUT_DIR / "task_period_gaps_min100.csv",
    index=False
)

print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print("outputs/task_panel_all.csv")
print("outputs/tasks_all_three_periods.csv")
print("outputs/tasks_all_three_periods_min100.csv")
print("outputs/balanced_task_panel_min100.csv")
print("outputs/balanced_panel_period_summary.csv")
print("outputs/balanced_panel_gap_summary.csv")
print("outputs/task_period_gaps_min100.csv")

print("\nDone!")