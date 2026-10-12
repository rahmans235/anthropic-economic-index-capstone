from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

PANEL_FILE = OUTPUT_DIR / "task_panel_all.csv"

# Minimum-count thresholds to test
THRESHOLDS = [50, 100, 250, 500, 1000]

# --------------------------------------------------
# Load the full task panel
# --------------------------------------------------

panel = pd.read_csv(PANEL_FILE)

# Add chronological order for the three periods
period_order = {
    "Aug 2025": 1,
    "Nov 2025": 2,
    "Feb 2026": 3,
}

panel["period_order"] = panel["period"].map(period_order)

# Check that every period was recognized
if panel["period_order"].isna().any():

    unknown_periods = panel.loc[
        panel["period_order"].isna(),
        "period"
    ].unique()

    raise ValueError(
        f"Unrecognized period labels: {unknown_periods}"
    )

print("=" * 80)
print("SENSITIVITY ANALYSIS")
print("=" * 80)

print(f"\nRows in full panel: {len(panel):,}")
print(f"Unique tasks overall: {panel['task'].nunique():,}")

# --------------------------------------------------
# Identify tasks appearing in all six combinations
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

fully_matched = coverage[
    (coverage["observations"] == 6)
    & (coverage["periods"] == 3)
    & (coverage["platforms"] == 2)
].copy()

print(
    "\nTasks appearing on both platforms "
    f"in all 3 periods: {len(fully_matched):,}"
)

# --------------------------------------------------
# Run analysis for each threshold
# --------------------------------------------------

results = []
direction_results = []

for threshold in THRESHOLDS:

    eligible = fully_matched[
        fully_matched["minimum_count"] >= threshold
    ].copy()

    threshold_panel = panel[
        panel["task"].isin(eligible["task"])
    ].copy()

    # Reshape so API and Claude.ai are side by side
    wide = threshold_panel.pivot(
        index=["task", "period_order", "period"],
        columns="platform",
        values="automation_pct"
    ).reset_index()

    wide["gap_pp"] = (
        wide["API"] - wide["Claude.ai"]
    )

    # --------------------------------------------------
    # Summaries for each period
    # --------------------------------------------------

    for (p_order, period), group in wide.groupby(
        ["period_order", "period"]
    ):

        api_higher = (group["gap_pp"] > 0).sum()
        claude_higher = (group["gap_pp"] < 0).sum()
        equal = (group["gap_pp"] == 0).sum()

        results.append(
            {
                "threshold": threshold,
                "period_order": p_order,
                "period": period,
                "tasks": len(group),
                "mean_gap_pp": group["gap_pp"].mean(),
                "median_gap_pp": group["gap_pp"].median(),
                "api_higher_tasks": api_higher,
                "claude_higher_tasks": claude_higher,
                "equal_tasks": equal,
                "api_higher_pct": (
                    100 * api_higher / len(group)
                    if len(group) > 0
                    else None
                )
            }
        )

    # --------------------------------------------------
    # Change from August to February
    # --------------------------------------------------

    gap_by_period = wide.pivot(
        index="task",
        columns="period",
        values="gap_pp"
    ).reset_index()

    if (
        "Aug 2025" in gap_by_period.columns
        and "Feb 2026" in gap_by_period.columns
    ):

        gap_by_period["gap_change_aug_to_feb"] = (
            gap_by_period["Feb 2026"]
            - gap_by_period["Aug 2025"]
        )

        narrower = (
            gap_by_period["gap_change_aug_to_feb"] < 0
        ).sum()

        wider = (
            gap_by_period["gap_change_aug_to_feb"] > 0
        ).sum()

        unchanged = (
            gap_by_period["gap_change_aug_to_feb"] == 0
        ).sum()

        direction_results.append(
            {
                "threshold": threshold,
                "tasks": len(gap_by_period),
                "mean_gap_change_aug_to_feb": (
                    gap_by_period[
                        "gap_change_aug_to_feb"
                    ].mean()
                ),
                "median_gap_change_aug_to_feb": (
                    gap_by_period[
                        "gap_change_aug_to_feb"
                    ].median()
                ),
                "tasks_gap_narrowed": narrower,
                "tasks_gap_widened": wider,
                "tasks_gap_unchanged": unchanged,
                "pct_gap_narrowed": (
                    100 * narrower / len(gap_by_period)
                    if len(gap_by_period) > 0
                    else None
                )
            }
        )

# --------------------------------------------------
# Create result tables
# --------------------------------------------------

results_df = pd.DataFrame(results)
direction_df = pd.DataFrame(direction_results)

# --------------------------------------------------
# Print number of tasks at each threshold
# --------------------------------------------------

print("\n" + "=" * 80)
print("NUMBER OF TASKS BY MINIMUM-COUNT THRESHOLD")
print("=" * 80)

threshold_counts = (
    results_df[
        ["threshold", "tasks"]
    ]
    .drop_duplicates()
    .sort_values("threshold")
)

print(threshold_counts.to_string(index=False))

# --------------------------------------------------
# Print mean automation gaps
# --------------------------------------------------

print("\n" + "=" * 80)
print("MEAN API - CLAUDE.AI GAP BY THRESHOLD AND PERIOD")
print("=" * 80)

gap_table = results_df.pivot(
    index="threshold",
    columns="period",
    values="mean_gap_pp"
)

gap_table = gap_table[
    ["Aug 2025", "Nov 2025", "Feb 2026"]
]

print(gap_table.round(3).to_string())

# --------------------------------------------------
# Print percent of tasks where API is higher
# --------------------------------------------------

print("\n" + "=" * 80)
print("PERCENT OF TASKS WITH HIGHER API AUTOMATION")
print("=" * 80)

api_table = results_df.pivot(
    index="threshold",
    columns="period",
    values="api_higher_pct"
)

api_table = api_table[
    ["Aug 2025", "Nov 2025", "Feb 2026"]
]

print(api_table.round(2).to_string())

# --------------------------------------------------
# Print August-to-February change
# --------------------------------------------------

print("\n" + "=" * 80)
print("CHANGE IN GAP: AUGUST 2025 TO FEBRUARY 2026")
print("=" * 80)

print(
    direction_df.round(3).to_string(index=False)
)

# --------------------------------------------------
# Save results
# --------------------------------------------------

results_df.to_csv(
    OUTPUT_DIR / "sensitivity_by_threshold.csv",
    index=False
)

direction_df.to_csv(
    OUTPUT_DIR / "sensitivity_gap_change.csv",
    index=False
)

print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print("outputs/sensitivity_by_threshold.csv")
print("outputs/sensitivity_gap_change.csv")

print("\nDone!")