from pathlib import Path
import pandas as pd

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

api_file = DATA_DIR / "aei_raw_1p_api_2025-08-04_to_2025-08-11.csv"
claude_file = DATA_DIR / "aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv"

# Load datasets
api = pd.read_csv(api_file)
claude = pd.read_csv(claude_file)

print("=" * 70)
print("STEP 5: RECORD INSPECTION")
print("=" * 70)

# --------------------------------------------------
# API RECORDS
# --------------------------------------------------

print("\n1P API RECORDS")

# Global directive collaboration record
api_directive = api[
    (api["geo_id"] == "GLOBAL")
    & (api["facet"] == "collaboration")
    & (api["variable"] == "collaboration_pct")
    & (api["cluster_name"] == "directive")
]

print("\nRECORD 1: API - Directive")
print(api_directive.to_string(index=False))


# Global feedback-loop collaboration record
api_feedback = api[
    (api["geo_id"] == "GLOBAL")
    & (api["facet"] == "collaboration")
    & (api["variable"] == "collaboration_pct")
    & (api["cluster_name"] == "feedback loop")
]

print("\nRECORD 2: API - Feedback Loop")
print(api_feedback.to_string(index=False))


# Largest classified API O*NET task
api_tasks = api[
    (api["geo_id"] == "GLOBAL")
    & (api["facet"] == "onet_task")
    & (api["variable"] == "onet_task_pct")
    & (~api["cluster_name"].isin(["none", "not_classified"]))
]

api_top_task = api_tasks.sort_values(
    "value", ascending=False
).head(1)

print("\nRECORD 3: API - Largest Classified O*NET Task")
print(api_top_task.to_string(index=False))


# --------------------------------------------------
# CLAUDE.AI RECORDS
# --------------------------------------------------

print("\n" + "=" * 70)
print("CLAUDE.AI RECORDS")

# Global directive collaboration record
claude_directive = claude[
    (claude["geo_id"] == "GLOBAL")
    & (claude["facet"] == "collaboration")
    & (claude["variable"] == "collaboration_pct")
    & (claude["cluster_name"] == "directive")
]

print("\nRECORD 4: Claude.ai - Directive")
print(claude_directive.to_string(index=False))


# Global task-iteration collaboration record
claude_iteration = claude[
    (claude["geo_id"] == "GLOBAL")
    & (claude["facet"] == "collaboration")
    & (claude["variable"] == "collaboration_pct")
    & (claude["cluster_name"] == "task iteration")
]

print("\nRECORD 5: Claude.ai - Task Iteration")
print(claude_iteration.to_string(index=False))


# Largest classified Claude.ai O*NET task
claude_tasks = claude[
    (claude["geo_id"] == "GLOBAL")
    & (claude["facet"] == "onet_task")
    & (claude["variable"] == "onet_task_pct")
    & (~claude["cluster_name"].isin(["none", "not_classified"]))
]

claude_top_task = claude_tasks.sort_values(
    "value", ascending=False
).head(1)

print("\nRECORD 6: Claude.ai - Largest Classified O*NET Task")
print(claude_top_task.to_string(index=False))

print("\n" + "=" * 70)
print("END OF RECORD INSPECTION")
print("=" * 70)