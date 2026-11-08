
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
FIG = ROOT / "figures"

OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

MATCHES_FILE = OUT / "task_occupation_matches.csv"
DECOMP_FILE = OUT / "gap_change_decomposition.csv"

# ============================================================
# BROAD SOC OCCUPATION GROUPS
# ============================================================

SOC_GROUPS = {
    "11": "Management",
    "13": "Business and Financial",
    "15": "Computer and Mathematical",
    "17": "Architecture and Engineering",
    "19": "Life, Physical, and Social Science",
    "21": "Community and Social Service",
    "23": "Legal",
    "25": "Educational Instruction and Library",
    "27": "Arts, Design, Entertainment, and Media",
    "29": "Healthcare Practitioners and Technical",
    "31": "Healthcare Support",
    "33": "Protective Service",
    "35": "Food Preparation and Serving",
    "37": "Building and Grounds Maintenance",
    "39": "Personal Care and Service",
    "41": "Sales and Related",
    "43": "Office and Administrative Support",
    "45": "Farming, Fishing, and Forestry",
    "47": "Construction and Extraction",
    "49": "Installation, Maintenance, and Repair",
    "51": "Production",
    "53": "Transportation and Material Moving",
    "55": "Military Specific"
}

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 65)
print("OCCUPATION-GROUP AUTOMATION ANALYSIS")
print("=" * 65)

matches = pd.read_csv(MATCHES_FILE)
decomp = pd.read_csv(DECOMP_FILE)

required_match_cols = {"task", "occupation_code"}
required_decomp_cols = {
    "task",
    "api_change_pp",
    "claude_change_pp",
    "gap_change_pp"
}

if not required_match_cols.issubset(matches.columns):
    raise ValueError(
        f"Mapping columns: {matches.columns.tolist()}"
    )

if not required_decomp_cols.issubset(decomp.columns):
    raise ValueError(
        f"Decomposition columns: {decomp.columns.tolist()}"
    )

if decomp["task"].duplicated().any():
    raise ValueError(
        "Expected one decomposition row per task."
    )

# ============================================================
# BUILD UNIQUE OCCUPATION MATCHES
# ============================================================

valid_matches = matches.dropna(
    subset=["occupation_code"]
).copy()

valid_matches["occupation_code"] = (
    valid_matches["occupation_code"].astype(str).str.strip()
)

valid_matches = valid_matches.drop_duplicates(
    subset=["task", "occupation_code"]
)

occupation_counts = (
    valid_matches.groupby("task")["occupation_code"]
    .nunique()
)

unique_tasks = occupation_counts[
    occupation_counts == 1
].index

unique_matches = valid_matches[
    valid_matches["task"].isin(unique_tasks)
].copy()

unique_matches["soc_major"] = (
    unique_matches["occupation_code"].str[:2]
)

unique_matches["occupation_group"] = (
    unique_matches["soc_major"].map(SOC_GROUPS)
)

if unique_matches["occupation_group"].isna().any():
    missing = unique_matches.loc[
        unique_matches["occupation_group"].isna(),
        "occupation_code"
    ].unique()

    raise ValueError(
        f"Unrecognized SOC codes: {missing}"
    )

# ============================================================
# JOIN WITH AUTOMATION-GAP CHANGES
# ============================================================

analysis = unique_matches.merge(
    decomp,
    on="task",
    how="inner",
    validate="one_to_one"
)

print(f"\nTotal tasks in main panel: {len(decomp)}")
print(f"Tasks with exactly one occupation: {len(unique_tasks)}")
print(f"Tasks included in group analysis: {len(analysis)}")

if len(analysis) != len(unique_tasks):
    raise ValueError(
        "Some uniquely mapped tasks are missing "
        "from the decomposition results."
    )

analysis.to_csv(
    OUT / "occupation_group_task_data.csv",
    index=False
)

# ============================================================
# SUMMARIZE BY OCCUPATION GROUP
# ============================================================

group_summary = (
    analysis.groupby("occupation_group")
    .agg(
        n_tasks=("task", "nunique"),
        mean_api_change_pp=("api_change_pp", "mean"),
        mean_claude_change_pp=("claude_change_pp", "mean"),
        mean_gap_change_pp=("gap_change_pp", "mean"),
        median_gap_change_pp=("gap_change_pp", "median"),
        std_gap_change_pp=("gap_change_pp", "std"),
        pct_tasks_narrowed=(
            "gap_change_pp",
            lambda x: 100 * (x < 0).mean()
        )
    )
    .reset_index()
    .sort_values("mean_gap_change_pp")
)

group_summary.to_csv(
    OUT / "occupation_group_summary.csv",
    index=False
)

print("\n" + "=" * 65)
print("OCCUPATION GROUP RESULTS")
print("=" * 65)

print(
    group_summary[
        [
            "occupation_group",
            "n_tasks",
            "mean_gap_change_pp",
            "pct_tasks_narrowed"
        ]
    ].round(2).to_string(index=False)
)

# ============================================================
# FIGURE: GROUP GAP CHANGES
# ============================================================

# Only plot groups with at least 5 tasks.
# This is a display threshold, not a significance test.

plot_data = group_summary[
    group_summary["n_tasks"] >= 5
].sort_values("mean_gap_change_pp")

if len(plot_data) > 0:
    fig, ax = plt.subplots(
        figsize=(11, max(5, 0.48 * len(plot_data)))
    )

    colors = np.where(
        plot_data["mean_gap_change_pp"] < 0,
        "#4472C4",
        "#E07A5F"
    )

    ax.barh(
        plot_data["occupation_group"],
        plot_data["mean_gap_change_pp"],
        color=colors
    )

    ax.axvline(0, color="black", linewidth=1)

    ax.set_xlabel(
        "Average change in API–Claude.ai automation gap "
        "(percentage points)"
    )

    ax.set_title(
        "Automation-Gap Change by Occupation Group\n"
        "August 2025 to February 2026"
    )

    ax.invert_yaxis()

    for i, row in enumerate(plot_data.itertuples()):
        value = row.mean_gap_change_pp
        offset = 0.35 if value >= 0 else -0.35
        ha = "left" if value >= 0 else "right"

        ax.text(
            value + offset,
            i,
            f"{value:+.1f} pp (n={row.n_tasks})",
            va="center",
            ha=ha,
            fontsize=9
        )

    ax.margins(x=0.20)
    plt.tight_layout()

    figure_path = (
        FIG / "occupation_group_gap_changes.png"
    )

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"\nSaved figure: {figure_path.name}")
else:
    print("\nNo occupation groups met the plot threshold.")

# ============================================================
# SENSITIVITY CHECK:
# INCLUDE TASKS MATCHED TO MULTIPLE OCCUPATIONS
# ============================================================

# Each task contributes total weight 1, split equally across
# its distinct occupations. If multiple occupations fall in
# the same broad group, their weights are combined.

all_matches = valid_matches.copy()

all_matches["occupation_count"] = (
    all_matches.groupby("task")["occupation_code"]
    .transform("nunique")
)

all_matches["weight"] = (
    1.0 / all_matches["occupation_count"]
)

all_matches["soc_major"] = (
    all_matches["occupation_code"].str[:2]
)

all_matches["occupation_group"] = (
    all_matches["soc_major"].map(SOC_GROUPS)
)

if all_matches["occupation_group"].isna().any():
    raise ValueError(
        "Unrecognized SOC group in sensitivity analysis."
    )

all_analysis = all_matches.merge(
    decomp,
    on="task",
    how="inner",
    validate="many_to_one"
)

def weighted_group_summary(group):
    w = group["weight"].to_numpy()
    y = group["gap_change_pp"].to_numpy()

    return pd.Series({
        "n_distinct_tasks": group["task"].nunique(),
        "effective_task_weight": w.sum(),
        "weighted_mean_gap_change_pp": np.average(
            y, weights=w
        )
    })

sensitivity = (
    all_analysis.groupby("occupation_group")
    .apply(weighted_group_summary)
    .reset_index()
)

comparison = group_summary[
    [
        "occupation_group",
        "n_tasks",
        "mean_gap_change_pp"
    ]
].merge(
    sensitivity,
    on="occupation_group",
    how="outer"
)

comparison["difference_pp"] = (
    comparison["weighted_mean_gap_change_pp"]
    - comparison["mean_gap_change_pp"]
)

comparison.to_csv(
    OUT / "occupation_group_sensitivity.csv",
    index=False
)

print("\n" + "=" * 65)
print("SENSITIVITY CHECK")
print("=" * 65)

print(
    comparison[
        [
            "occupation_group",
            "n_tasks",
            "mean_gap_change_pp",
            "weighted_mean_gap_change_pp",
            "difference_pp"
        ]
    ].round(2).to_string(index=False)
)

print("\n" + "=" * 65)
print("ANALYSIS COMPLETE")
print("=" * 65)

print("\nSaved files:")
print("outputs/occupation_group_task_data.csv")
print("outputs/occupation_group_summary.csv")
print("outputs/occupation_group_sensitivity.csv")
print("figures/occupation_group_gap_changes.png")
