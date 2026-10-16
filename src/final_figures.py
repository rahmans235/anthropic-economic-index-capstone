from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = PROJECT_ROOT / "figures"

FIGURE_DIR.mkdir(exist_ok=True)

PANEL_FILE = OUTPUT_DIR / "balanced_task_panel_min100.csv"
GAP_FILE = OUTPUT_DIR / "paired_task_gap_changes.csv"


# ============================================================
# LOAD DATA
# ============================================================

panel = pd.read_csv(PANEL_FILE)
gaps = pd.read_csv(GAP_FILE)

period_order = [
    "Aug 2025",
    "Nov 2025",
    "Feb 2026",
]


# ============================================================
# FIGURE 1:
# MEAN AUTOMATION BY PLATFORM OVER TIME
# ============================================================

summary = (
    panel
    .groupby(
        ["period", "platform"],
        observed=True
    )["automation_pct"]
    .mean()
    .reset_index()
)

summary["period"] = pd.Categorical(
    summary["period"],
    categories=period_order,
    ordered=True
)

summary = summary.sort_values("period")


plt.figure(figsize=(8, 5))

for platform in ["API", "Claude.ai"]:

    subset = summary[
        summary["platform"] == platform
    ]

    plt.plot(
        subset["period"],
        subset["automation_pct"],
        marker="o",
        linewidth=2,
        label=platform
    )

plt.xlabel("Period")
plt.ylabel("Mean Automation (%)")

plt.title(
    "Mean Automation by Platform Over Time\n"
    "352 Matched Tasks"
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.25
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR /
    "automation_by_platform_over_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 2:
# API - CLAUDE.AI GAP OVER TIME
# ============================================================

gap_summary = (
    panel
    .pivot_table(
        index=["task", "period"],
        columns="platform",
        values="automation_pct"
    )
    .reset_index()
)

gap_summary["gap_pp"] = (
    gap_summary["API"]
    - gap_summary["Claude.ai"]
)

mean_gaps = (
    gap_summary
    .groupby(
        "period",
        observed=True
    )["gap_pp"]
    .mean()
    .reindex(period_order)
)


plt.figure(figsize=(8, 5))

plt.plot(
    period_order,
    mean_gaps.values,
    marker="o",
    linewidth=2
)

for period, value in zip(
    period_order,
    mean_gaps.values
):
    plt.annotate(
        f"{value:.1f} pp",
        (period, value),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center"
    )

plt.xlabel("Period")

plt.ylabel(
    "Mean API - Claude.ai Automation Gap\n"
    "(percentage points)"
)

plt.title(
    "Automation Gap Between API and Claude.ai\n"
    "352 Matched Tasks"
)

# Give the labels extra space above and below.
# This prevents the November 29.5 pp label from
# getting too close to the top of the graph.
plt.ylim(
    mean_gaps.min() - 1,
    mean_gaps.max() + 1
)

plt.grid(
    axis="y",
    alpha=0.25
)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR /
    "automation_gap_over_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 3:
# DISTRIBUTION OF AUGUST -> FEBRUARY GAP CHANGES
# ============================================================

change = gaps["change_aug_to_feb"]


plt.figure(figsize=(8, 5))

plt.hist(
    change,
    bins=30,
    edgecolor="black",
    alpha=0.8
)

plt.axvline(
    0,
    linestyle="--",
    linewidth=2,
    label="No change"
)

plt.axvline(
    change.mean(),
    linestyle="-",
    linewidth=2,
    label=(
        f"Mean change = "
        f"{change.mean():.1f} pp"
    )
)

plt.xlabel(
    "Change in API - Claude.ai Gap\n"
    "(February minus August, percentage points)"
)

plt.ylabel("Number of Tasks")

plt.title(
    "Change in Automation Gap from August to February\n"
    "352 Matched Tasks"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    FIGURE_DIR /
    "aug_to_feb_gap_change_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# PRINT SUMMARY
# ============================================================

print("=" * 80)
print("FINAL FIGURES")
print("=" * 80)

print("\nMean automation percentages:")

print(
    summary
    .pivot(
        index="period",
        columns="platform",
        values="automation_pct"
    )
    .reindex(period_order)
    .round(3)
)


print("\nMean API - Claude.ai gaps:")

for period in period_order:

    print(
        f"{period}: "
        f"{mean_gaps.loc[period]:.3f} pp"
    )


print(
    "\nAugust -> February mean gap change: "
    f"{change.mean():.3f} pp"
)

print(
    "August -> February median gap change: "
    f"{change.median():.3f} pp"
)


print("\nFiles saved:")

print(
    "figures/automation_by_platform_over_time.png"
)

print(
    "figures/automation_gap_over_time.png"
)

print(
    "figures/aug_to_feb_gap_change_distribution.png"
)

print("\nDone!")