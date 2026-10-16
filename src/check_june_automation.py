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
# June release files
# --------------------------------------------------

FILES = [
    (
        "API",
        DATA_DIR / "aei_1p_api_2026-06-26.csv"
    ),
    (
        "Claude.ai",
        DATA_DIR / "aei_claude_ai_2026-06-26.csv"
    ),
]

# Metrics we need
METRICS = [
    "collaboration_directive_pct",
    "collaboration_feedback_loop_pct",
    "collaboration_bucket_automation_pct",
]

all_results = []

print("=" * 80)
print("JUNE 2026 AUTOMATION COMPATIBILITY CHECK")
print("=" * 80)

# --------------------------------------------------
# Process each platform
# --------------------------------------------------

for platform, file_path in FILES:

    print("\n" + "=" * 80)
    print(f"PLATFORM: {platform}")
    print("=" * 80)

    df = pd.read_csv(file_path, low_memory=False)

    # --------------------------------------------------
    # Keep global O*NET task-level records only
    # --------------------------------------------------
    #
    # hierarchy_level == 0 corresponds to the
    # task-level O*NET records we want to compare
    # with the earlier task analysis.
    # --------------------------------------------------

    tasks = df[
        (df["geo_id"] == "GLOBAL")
        & (df["category_name"] == "onet")
        & (df["hierarchy_level"] == 0)
        & (df["metric_id"].isin(METRICS))
    ].copy()

    print(
        f"\nRelevant global task-level rows: "
        f"{len(tasks):,}"
    )

    print("\nDates found:")
    print(
        tasks[
            ["date_start", "date_end"]
        ]
        .drop_duplicates()
        .sort_values("date_start")
        .to_string(index=False)
    )

    print("\nMetric counts:")
    print(
        tasks["metric_id"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------
    # Put the three metrics side-by-side
    # --------------------------------------------------

    wide = tasks.pivot_table(
        index=[
            "date_start",
            "date_end",
            "node_external_id",
            "node_name",
        ],
        columns="metric_id",
        values="value",
        aggfunc="first"
    ).reset_index()

    # --------------------------------------------------
    # Require all three measurements
    # --------------------------------------------------

    complete = wide.dropna(
        subset=METRICS
    ).copy()

    print(
        f"\nTask-month rows with all 3 metrics: "
        f"{len(complete):,}"
    )

    # --------------------------------------------------
    # Reconstruct automation ourselves
    # --------------------------------------------------

    complete["calculated_automation_pct"] = (
        complete["collaboration_directive_pct"]
        + complete["collaboration_feedback_loop_pct"]
    )

    # Difference:
    # released automation bucket minus our calculation
    complete["difference_pp"] = (
        complete["collaboration_bucket_automation_pct"]
        - complete["calculated_automation_pct"]
    )

    complete["absolute_difference_pp"] = (
        complete["difference_pp"].abs()
    )

    complete["platform"] = platform

    all_results.append(complete)

    # --------------------------------------------------
    # Summaries
    # --------------------------------------------------

    print("\nDIFFERENCE SUMMARY:")
    print(
        complete["difference_pp"]
        .describe()
        .to_string()
    )

    print("\nABSOLUTE DIFFERENCE SUMMARY:")
    print(
        complete["absolute_difference_pp"]
        .describe()
        .to_string()
    )

    # Allow tiny differences from percentages being
    # rounded to two decimal places.
    within_001 = (
        complete["absolute_difference_pp"] <= 0.01
    ).sum()

    within_002 = (
        complete["absolute_difference_pp"] <= 0.02
    ).sum()

    within_005 = (
        complete["absolute_difference_pp"] <= 0.05
    ).sum()

    total = len(complete)

    print("\nROUNDING CHECK:")

    print(
        f"Within 0.01 percentage points: "
        f"{within_001:,}/{total:,} "
        f"({100 * within_001 / total:.2f}%)"
    )

    print(
        f"Within 0.02 percentage points: "
        f"{within_002:,}/{total:,} "
        f"({100 * within_002 / total:.2f}%)"
    )

    print(
        f"Within 0.05 percentage points: "
        f"{within_005:,}/{total:,} "
        f"({100 * within_005 / total:.2f}%)"
    )

    # --------------------------------------------------
    # Largest discrepancies
    # --------------------------------------------------

    print("\n10 LARGEST ABSOLUTE DIFFERENCES:")

    largest = (
        complete
        .sort_values(
            "absolute_difference_pp",
            ascending=False
        )
        .head(10)
    )

    print(
        largest[
            [
                "date_start",
                "node_name",
                "collaboration_directive_pct",
                "collaboration_feedback_loop_pct",
                "calculated_automation_pct",
                "collaboration_bucket_automation_pct",
                "difference_pp",
            ]
        ].to_string(index=False)
    )

# --------------------------------------------------
# Combine both platforms
# --------------------------------------------------

results = pd.concat(
    all_results,
    ignore_index=True
)

# --------------------------------------------------
# Summary by platform and month
# --------------------------------------------------

summary = (
    results
    .groupby(
        ["platform", "date_start"]
    )
    .agg(
        tasks=("node_name", "size"),
        mean_difference_pp=(
            "difference_pp",
            "mean"
        ),
        mean_absolute_difference_pp=(
            "absolute_difference_pp",
            "mean"
        ),
        max_absolute_difference_pp=(
            "absolute_difference_pp",
            "max"
        )
    )
    .reset_index()
)

print("\n" + "=" * 80)
print("SUMMARY BY PLATFORM AND MONTH")
print("=" * 80)

print(
    summary
    .round(4)
    .to_string(index=False)
)

# --------------------------------------------------
# Overall compatibility decision
# --------------------------------------------------

max_difference = (
    results["absolute_difference_pp"].max()
)

mean_difference = (
    results["absolute_difference_pp"].mean()
)

print("\n" + "=" * 80)
print("OVERALL CHECK")
print("=" * 80)

print(
    f"Mean absolute difference: "
    f"{mean_difference:.4f} percentage points"
)

print(
    f"Maximum absolute difference: "
    f"{max_difference:.4f} percentage points"
)

if max_difference <= 0.02:

    print(
        "\nRESULT: The released automation bucket "
        "matches directive + feedback loop within "
        "normal rounding error."
    )

else:

    print(
        "\nRESULT: Some differences are larger than "
        "normal rounding error. Inspect before "
        "treating the measures as equivalent."
    )

# --------------------------------------------------
# Save results
# --------------------------------------------------

results.to_csv(
    OUTPUT_DIR /
    "june_automation_compatibility.csv",
    index=False
)

summary.to_csv(
    OUTPUT_DIR /
    "june_automation_compatibility_summary.csv",
    index=False
)

print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print(
    "outputs/june_automation_compatibility.csv"
)

print(
    "outputs/june_automation_compatibility_summary.csv"
)

print("\nDone!")