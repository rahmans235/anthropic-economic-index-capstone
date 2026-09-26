
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "outputs"

comparison_file = (
    OUTPUT_DIR / "matched_tasks_min100.csv"
)

# --------------------------------------------------
# Load matched-task comparison
# --------------------------------------------------

df = pd.read_csv(comparison_file)

print("=" * 80)
print("TASK-LEVEL AUTOMATION GAP ANALYSIS")
print("=" * 80)

print(f"\nNumber of matched tasks: {len(df):,}")

# --------------------------------------------------
# Tasks where Claude.ai has higher automation
# --------------------------------------------------

claude_higher = df[
    df["gap_pp"] < 0
].sort_values(
    "gap_pp",
    ascending=True
)

print("\n" + "=" * 80)
print("TASKS WHERE CLAUDE.AI AUTOMATION IS HIGHER")
print("=" * 80)

print(
    claude_higher[
        [
            "task",
            "total_count_api",
            "total_count_claude",
            "automation_pct_api",
            "automation_pct_claude",
            "gap_pp",
        ]
    ].to_string(index=False)
)

# --------------------------------------------------
# Tasks with the largest API automation gaps
# --------------------------------------------------

largest_api_gaps = df.sort_values(
    "gap_pp",
    ascending=False
).head(15)

print("\n" + "=" * 80)
print("15 TASKS WITH THE LARGEST API AUTOMATION GAPS")
print("=" * 80)

print(
    largest_api_gaps[
        [
            "task",
            "total_count_api",
            "total_count_claude",
            "automation_pct_api",
            "automation_pct_claude",
            "gap_pp",
        ]
    ].to_string(index=False)
)

# --------------------------------------------------
# Tasks with the smallest absolute gaps
# --------------------------------------------------

df["absolute_gap"] = df["gap_pp"].abs()

smallest_gaps = df.sort_values(
    "absolute_gap",
    ascending=True
).head(15)

print("\n" + "=" * 80)
print("15 TASKS WITH THE SMALLEST AUTOMATION GAPS")
print("=" * 80)

print(
    smallest_gaps[
        [
            "task",
            "total_count_api",
            "total_count_claude",
            "automation_pct_api",
            "automation_pct_claude",
            "gap_pp",
        ]
    ].to_string(index=False)
)

# --------------------------------------------------
# Save results
# --------------------------------------------------

claude_higher.to_csv(
    OUTPUT_DIR / "claude_higher_automation.csv",
    index=False
)

largest_api_gaps.to_csv(
    OUTPUT_DIR / "largest_api_automation_gaps.csv",
    index=False
)

smallest_gaps.to_csv(
    OUTPUT_DIR / "smallest_automation_gaps.csv",
    index=False
)

print("\n" + "=" * 80)
print("Results saved to outputs/")
print("=" * 80)