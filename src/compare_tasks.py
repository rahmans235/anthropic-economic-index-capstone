
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

api_file = DATA_DIR / "aei_raw_1p_api_2025-08-04_to_2025-08-11.csv"
claude_file = DATA_DIR / "aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv"

api = pd.read_csv(api_file)
claude = pd.read_csv(claude_file)

# Collaboration styles classified as automation
AUTOMATION = ["directive", "feedback loop"]


# --------------------------------------------------
# Calculate automation percentage for every task
# --------------------------------------------------

def calculate_task_automation(df, platform):

    tasks = df[
        (df["geo_id"] == "GLOBAL")
        & (df["facet"] == "onet_task::collaboration")
        & (df["variable"] == "onet_task_collaboration_count")
    ].copy()

    # Split the combined task/collaboration label
    tasks[["task", "collaboration"]] = (
        tasks["cluster_name"].str.rsplit(
            "::",
            n=1,
            expand=True
        )
    )

    # --------------------------------------------------
    # NEW: Exclude unclassified O*NET tasks
    # --------------------------------------------------

    tasks = tasks[
        ~tasks["task"].isin(
            ["none", "not_classified"]
        )
    ].copy()

    # --------------------------------------------------
    # Identify automation-oriented records
    # --------------------------------------------------

    tasks["automation_count"] = tasks["value"].where(
        tasks["collaboration"].isin(AUTOMATION),
        0
    )

    # --------------------------------------------------
    # Aggregate within each task
    # --------------------------------------------------

    summary = tasks.groupby(
        "task",
        as_index=False
    ).agg(
        total_count=("value", "sum"),
        automation_count=("automation_count", "sum")
    )

    # Calculate task-specific automation percentage
    summary["automation_pct"] = (
        summary["automation_count"]
        / summary["total_count"]
        * 100
    )

    summary["platform"] = platform

    return summary


# --------------------------------------------------
# Calculate results for both platforms
# --------------------------------------------------

api_summary = calculate_task_automation(
    api,
    "API"
)

claude_summary = calculate_task_automation(
    claude,
    "Claude.ai"
)


# --------------------------------------------------
# Match identical tasks across platforms
# --------------------------------------------------

comparison = api_summary.merge(
    claude_summary,
    on="task",
    how="inner",
    suffixes=("_api", "_claude")
)

# API minus Claude.ai automation percentage
comparison["gap_pp"] = (
    comparison["automation_pct_api"]
    - comparison["automation_pct_claude"]
)


# --------------------------------------------------
# Flag tasks with sufficient counts
# --------------------------------------------------

MIN_COUNT = 100

comparison["sufficient_count"] = (
    (comparison["total_count_api"] >= MIN_COUNT)
    & (comparison["total_count_claude"] >= MIN_COUNT)
)

# Keep sufficiently represented tasks
reliable = comparison[
    comparison["sufficient_count"]
].copy()


# --------------------------------------------------
# Print summary
# --------------------------------------------------

print("=" * 70)
print("SAME-TASK AUTOMATION COMPARISON")
print("=" * 70)

print(f"\nUnique API tasks: {len(api_summary):,}")

print(
    f"Unique Claude.ai tasks: "
    f"{len(claude_summary):,}"
)

print(
    f"Tasks appearing on both platforms: "
    f"{len(comparison):,}"
)

print(
    f"Matched tasks with at least {MIN_COUNT} "
    f"observations on each platform: {len(reliable):,}"
)

print("\nGap summary for sufficiently represented tasks:")

print(
    reliable["gap_pp"].describe().to_string()
)

print("\nTasks with higher API automation:")

print(
    (reliable["gap_pp"] > 0).sum()
)

print("\nTasks with higher Claude.ai automation:")

print(
    (reliable["gap_pp"] < 0).sum()
)

print("\nTasks with equal automation rates:")

print(
    (reliable["gap_pp"] == 0).sum()
)


# --------------------------------------------------
# Show largest tasks by combined count
# --------------------------------------------------

reliable["combined_count"] = (
    reliable["total_count_api"]
    + reliable["total_count_claude"]
)

top_tasks = reliable.sort_values(
    "combined_count",
    ascending=False
).head(15)

print("\nTop 15 matched tasks by combined count:")

print(
    top_tasks[
        [
            "task",
            "total_count_api",
            "total_count_claude",
            "automation_pct_api",
            "automation_pct_claude",
            "gap_pp"
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# Save reproducible outputs
# --------------------------------------------------

comparison.to_csv(
    OUTPUT_DIR / "all_matched_tasks.csv",
    index=False
)

reliable.to_csv(
    OUTPUT_DIR / "matched_tasks_min100.csv",
    index=False
)

print("\nComparison tables saved to outputs/")

print("=" * 70)