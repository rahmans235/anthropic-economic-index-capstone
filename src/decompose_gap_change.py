from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

INPUT_FILE = OUTPUT_DIR / "balanced_task_panel_min100.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("DECOMPOSING THE AUGUST -> FEBRUARY GAP CHANGE")
print("=" * 80)

df = pd.read_csv(INPUT_FILE)

print(f"\nRows: {len(df):,}")
print(f"Unique tasks: {df['task'].nunique():,}")


# ============================================================
# KEEP AUGUST AND FEBRUARY
# ============================================================

analysis = df[
    df["period"].isin(
        ["Aug 2025", "Feb 2026"]
    )
].copy()

print(
    f"Rows used for Aug/Feb comparison: "
    f"{len(analysis):,}"
)


# ============================================================
# PUT PLATFORM/PERIOD VALUES SIDE BY SIDE
# ============================================================

wide = analysis.pivot(
    index="task",
    columns=["platform", "period"],
    values="automation_pct"
)

# Flatten the column names
wide.columns = [
    f"{platform}_{period}"
    for platform, period in wide.columns
]

wide = wide.reset_index()


# ============================================================
# CHECK EXPECTED COLUMNS
# ============================================================

required = [
    "API_Aug 2025",
    "API_Feb 2026",
    "Claude.ai_Aug 2025",
    "Claude.ai_Feb 2026",
]

missing = [
    column for column in required
    if column not in wide.columns
]

if missing:
    raise ValueError(
        f"Missing expected columns: {missing}"
    )

wide = wide.dropna(
    subset=required
).copy()

print(
    f"Complete tasks: {len(wide):,}"
)


# ============================================================
# CALCULATE PLATFORM-SPECIFIC CHANGES
# ============================================================

wide["api_change_pp"] = (
    wide["API_Feb 2026"]
    - wide["API_Aug 2025"]
)

wide["claude_change_pp"] = (
    wide["Claude.ai_Feb 2026"]
    - wide["Claude.ai_Aug 2025"]
)


# Gap in each period

wide["aug_gap_pp"] = (
    wide["API_Aug 2025"]
    - wide["Claude.ai_Aug 2025"]
)

wide["feb_gap_pp"] = (
    wide["API_Feb 2026"]
    - wide["Claude.ai_Feb 2026"]
)


# Change in the API-Claude gap

wide["gap_change_pp"] = (
    wide["feb_gap_pp"]
    - wide["aug_gap_pp"]
)


# Verify the decomposition:
#
# gap change =
# API change - Claude.ai change

wide["decomposition_check"] = (
    wide["api_change_pp"]
    - wide["claude_change_pp"]
)

if not np.allclose(
    wide["gap_change_pp"],
    wide["decomposition_check"],
):
    raise ValueError(
        "Gap decomposition check failed."
    )

print("\nGap decomposition check passed.")


# ============================================================
# SUMMARY FUNCTION
# ============================================================

def summarize_change(series, label):

    n = len(series)

    mean = series.mean()
    median = series.median()
    sd = series.std(ddof=1)
    se = sd / np.sqrt(n)

    t_critical = stats.t.ppf(
        0.975,
        df=n - 1
    )

    ci_lower = mean - t_critical * se
    ci_upper = mean + t_critical * se

    decreased = (series < 0).sum()
    increased = (series > 0).sum()
    unchanged = (series == 0).sum()

    print("\n" + "-" * 80)
    print(label)
    print("-" * 80)

    print(f"Mean change: {mean:.3f} pp")
    print(f"Median change: {median:.3f} pp")

    print(
        "95% CI for mean change: "
        f"[{ci_lower:.3f}, "
        f"{ci_upper:.3f}] pp"
    )

    print(
        f"Decreased: {decreased:,} "
        f"({100 * decreased / n:.2f}%)"
    )

    print(
        f"Increased: {increased:,} "
        f"({100 * increased / n:.2f}%)"
    )

    print(
        f"Unchanged: {unchanged:,} "
        f"({100 * unchanged / n:.2f}%)"
    )

    return {
        "measure": label,
        "n_tasks": n,
        "mean_change_pp": mean,
        "median_change_pp": median,
        "ci_lower_pp": ci_lower,
        "ci_upper_pp": ci_upper,
        "n_decreased": decreased,
        "pct_decreased":
            100 * decreased / n,
        "n_increased": increased,
        "pct_increased":
            100 * increased / n,
        "n_unchanged": unchanged,
    }


# ============================================================
# SUMMARIZE API, CLAUDE, AND GAP CHANGES
# ============================================================

summary_rows = []

summary_rows.append(
    summarize_change(
        wide["api_change_pp"],
        "API automation change"
    )
)

summary_rows.append(
    summarize_change(
        wide["claude_change_pp"],
        "Claude.ai automation change"
    )
)

summary_rows.append(
    summarize_change(
        wide["gap_change_pp"],
        "API - Claude.ai gap change"
    )
)

summary = pd.DataFrame(summary_rows)


# ============================================================
# CLASSIFY HOW EACH TASK CHANGED
# ============================================================
#
# This tells us whether automation increased or decreased
# on each platform.
#
# ============================================================

conditions = [
    (
        (wide["api_change_pp"] < 0)
        & (wide["claude_change_pp"] < 0)
    ),
    (
        (wide["api_change_pp"] < 0)
        & (wide["claude_change_pp"] > 0)
    ),
    (
        (wide["api_change_pp"] > 0)
        & (wide["claude_change_pp"] < 0)
    ),
    (
        (wide["api_change_pp"] > 0)
        & (wide["claude_change_pp"] > 0)
    ),
]

labels = [
    "Both decreased",
    "API decreased, Claude.ai increased",
    "API increased, Claude.ai decreased",
    "Both increased",
]

wide["change_pattern"] = np.select(
    conditions,
    labels,
    default="At least one unchanged"
)


# ============================================================
# PATTERN SUMMARY
# ============================================================

pattern_summary = (
    wide["change_pattern"]
    .value_counts()
    .rename_axis("change_pattern")
    .reset_index(name="n_tasks")
)

pattern_summary["percent"] = (
    100
    * pattern_summary["n_tasks"]
    / len(wide)
)


print("\n" + "=" * 80)
print("PLATFORM CHANGE PATTERNS")
print("=" * 80)

print(
    pattern_summary
    .round(2)
    .to_string(index=False)
)


# ============================================================
# WHAT HAPPENED WHEN THE GAP NARROWED?
# ============================================================

narrowed = wide[
    wide["gap_change_pp"] < 0
].copy()

widened = wide[
    wide["gap_change_pp"] > 0
].copy()


print("\n" + "=" * 80)
print("TASKS WHERE THE GAP NARROWED")
print("=" * 80)

print(f"\nNumber of tasks: {len(narrowed):,}")

print(
    "Mean API change: "
    f"{narrowed['api_change_pp'].mean():.3f} pp"
)

print(
    "Mean Claude.ai change: "
    f"{narrowed['claude_change_pp'].mean():.3f} pp"
)

print(
    "Mean gap change: "
    f"{narrowed['gap_change_pp'].mean():.3f} pp"
)


print("\n" + "=" * 80)
print("TASKS WHERE THE GAP WIDENED")
print("=" * 80)

print(f"\nNumber of tasks: {len(widened):,}")

print(
    "Mean API change: "
    f"{widened['api_change_pp'].mean():.3f} pp"
)

print(
    "Mean Claude.ai change: "
    f"{widened['claude_change_pp'].mean():.3f} pp"
)

print(
    "Mean gap change: "
    f"{widened['gap_change_pp'].mean():.3f} pp"
)


# ============================================================
# LARGEST NARROWING / WIDENING
# ============================================================

largest_narrowing = (
    wide
    .sort_values("gap_change_pp")
    .head(15)
)

largest_widening = (
    wide
    .sort_values(
        "gap_change_pp",
        ascending=False
    )
    .head(15)
)


print("\n" + "=" * 80)
print("10 TASKS WITH LARGEST GAP NARROWING")
print("=" * 80)

print(
    largest_narrowing[
        [
            "task",
            "api_change_pp",
            "claude_change_pp",
            "gap_change_pp",
        ]
    ]
    .head(10)
    .round(3)
    .to_string(index=False)
)


print("\n" + "=" * 80)
print("10 TASKS WITH LARGEST GAP WIDENING")
print("=" * 80)

print(
    largest_widening[
        [
            "task",
            "api_change_pp",
            "claude_change_pp",
            "gap_change_pp",
        ]
    ]
    .head(10)
    .round(3)
    .to_string(index=False)
)


# ============================================================
# SAVE OUTPUTS
# ============================================================

wide.to_csv(
    OUTPUT_DIR /
    "gap_change_decomposition.csv",
    index=False
)

summary.to_csv(
    OUTPUT_DIR /
    "gap_change_decomposition_summary.csv",
    index=False
)

pattern_summary.to_csv(
    OUTPUT_DIR /
    "gap_change_patterns.csv",
    index=False
)

largest_narrowing.to_csv(
    OUTPUT_DIR /
    "largest_gap_narrowing_tasks.csv",
    index=False
)

largest_widening.to_csv(
    OUTPUT_DIR /
    "largest_gap_widening_tasks.csv",
    index=False
)


print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print(
    "outputs/gap_change_decomposition.csv"
)

print(
    "outputs/gap_change_decomposition_summary.csv"
)

print(
    "outputs/gap_change_patterns.csv"
)

print(
    "outputs/largest_gap_narrowing_tasks.csv"
)

print(
    "outputs/largest_gap_widening_tasks.csv"
)

print("\nDone!")