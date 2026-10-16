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
print("PAIRED TASK-LEVEL GAP ANALYSIS")
print("=" * 80)

df = pd.read_csv(INPUT_FILE)

print(f"\nRows: {len(df):,}")
print(f"Unique tasks: {df['task'].nunique():,}")


# ============================================================
# CHECK DATA
# ============================================================

required_columns = [
    "task",
    "platform",
    "period",
    "automation_pct",
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

expected_periods = [
    "Aug 2025",
    "Nov 2025",
    "Feb 2026",
]

expected_platforms = [
    "API",
    "Claude.ai",
]

print("\nPeriods:")
print(df["period"].value_counts())

print("\nPlatforms:")
print(df["platform"].value_counts())


# ============================================================
# CREATE API - CLAUDE GAP FOR EACH TASK AND PERIOD
# ============================================================

wide_platform = df.pivot(
    index=["task", "period"],
    columns="platform",
    values="automation_pct",
).reset_index()

wide_platform["gap_pp"] = (
    wide_platform["API"]
    - wide_platform["Claude.ai"]
)

print("\nTask-period gap rows:")
print(f"{len(wide_platform):,}")


# ============================================================
# PUT PERIODS SIDE-BY-SIDE
# ============================================================

gaps = wide_platform.pivot(
    index="task",
    columns="period",
    values="gap_pp",
).reset_index()

# Make sure all periods exist
for period in expected_periods:
    if period not in gaps.columns:
        raise ValueError(
            f"Missing period: {period}"
        )

gaps = gaps.dropna(
    subset=expected_periods
).copy()

print(
    f"Tasks with all three gap measurements: "
    f"{len(gaps):,}"
)


# ============================================================
# CALCULATE CHANGES IN THE GAP
# ============================================================

# Negative change = gap narrowed
# Positive change = gap widened

gaps["change_aug_to_nov"] = (
    gaps["Nov 2025"]
    - gaps["Aug 2025"]
)

gaps["change_aug_to_feb"] = (
    gaps["Feb 2026"]
    - gaps["Aug 2025"]
)

gaps["change_nov_to_feb"] = (
    gaps["Feb 2026"]
    - gaps["Nov 2025"]
)


# ============================================================
# FUNCTION FOR PAIRED ANALYSIS
# ============================================================

def analyze_change(data, earlier, later):

    earlier_values = data[earlier]
    later_values = data[later]

    changes = (
        later_values - earlier_values
    )

    n = len(changes)

    mean_change = changes.mean()
    median_change = changes.median()
    sd_change = changes.std(ddof=1)
    se_change = sd_change / np.sqrt(n)

    # 95% confidence interval for mean change
    t_critical = stats.t.ppf(
        0.975,
        df=n - 1
    )

    ci_lower = (
        mean_change
        - t_critical * se_change
    )

    ci_upper = (
        mean_change
        + t_critical * se_change
    )

    # Paired t-test
    t_result = stats.ttest_rel(
        later_values,
        earlier_values
    )

    # Wilcoxon signed-rank test:
    # useful non-parametric robustness check
    wilcoxon_result = stats.wilcoxon(
        later_values,
        earlier_values,
        alternative="two-sided",
        zero_method="wilcox",
    )

    narrowed = (changes < 0).sum()
    widened = (changes > 0).sum()
    unchanged = (changes == 0).sum()

    print("\n" + "=" * 80)
    print(f"{earlier} -> {later}")
    print("=" * 80)

    print(f"\nNumber of tasks: {n:,}")

    print(
        f"Mean gap in {earlier}: "
        f"{earlier_values.mean():.3f} pp"
    )

    print(
        f"Mean gap in {later}: "
        f"{later_values.mean():.3f} pp"
    )

    print(
        f"\nMean change in gap: "
        f"{mean_change:.3f} pp"
    )

    print(
        f"Median change in gap: "
        f"{median_change:.3f} pp"
    )

    print(
        "95% CI for mean change: "
        f"[{ci_lower:.3f}, {ci_upper:.3f}] pp"
    )

    print("\nDirection:")

    print(
        f"Narrowed: {narrowed:,} "
        f"({100 * narrowed / n:.2f}%)"
    )

    print(
        f"Widened: {widened:,} "
        f"({100 * widened / n:.2f}%)"
    )

    print(
        f"Unchanged: {unchanged:,} "
        f"({100 * unchanged / n:.2f}%)"
    )

    print("\nPaired t-test:")

    print(
        f"t = {t_result.statistic:.4f}"
    )

    print(
        f"p = {t_result.pvalue:.6g}"
    )

    print("\nWilcoxon signed-rank test:")

    print(
        f"statistic = "
        f"{wilcoxon_result.statistic:.4f}"
    )

    print(
        f"p = "
        f"{wilcoxon_result.pvalue:.6g}"
    )

    return {
        "earlier_period": earlier,
        "later_period": later,
        "n_tasks": n,
        "mean_earlier_gap_pp":
            earlier_values.mean(),
        "mean_later_gap_pp":
            later_values.mean(),
        "mean_change_pp": mean_change,
        "median_change_pp": median_change,
        "ci_lower_pp": ci_lower,
        "ci_upper_pp": ci_upper,
        "n_narrowed": narrowed,
        "pct_narrowed":
            100 * narrowed / n,
        "n_widened": widened,
        "pct_widened":
            100 * widened / n,
        "n_unchanged": unchanged,
        "paired_t_statistic":
            t_result.statistic,
        "paired_t_p_value":
            t_result.pvalue,
        "wilcoxon_statistic":
            wilcoxon_result.statistic,
        "wilcoxon_p_value":
            wilcoxon_result.pvalue,
    }


# ============================================================
# RUN THREE PERIOD COMPARISONS
# ============================================================

results = []

results.append(
    analyze_change(
        gaps,
        "Aug 2025",
        "Nov 2025",
    )
)

results.append(
    analyze_change(
        gaps,
        "Aug 2025",
        "Feb 2026",
    )
)

results.append(
    analyze_change(
        gaps,
        "Nov 2025",
        "Feb 2026",
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

summary = pd.DataFrame(results)

gaps.to_csv(
    OUTPUT_DIR /
    "paired_task_gap_changes.csv",
    index=False
)

summary.to_csv(
    OUTPUT_DIR /
    "paired_gap_analysis_summary.csv",
    index=False
)


print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

display_columns = [
    "earlier_period",
    "later_period",
    "n_tasks",
    "mean_change_pp",
    "ci_lower_pp",
    "ci_upper_pp",
    "pct_narrowed",
    "paired_t_p_value",
    "wilcoxon_p_value",
]

print(
    summary[
        display_columns
    ]
    .round(4)
    .to_string(index=False)
)


print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print(
    "outputs/paired_task_gap_changes.csv"
)

print(
    "outputs/paired_gap_analysis_summary.csv"
)

print("\nDone!")