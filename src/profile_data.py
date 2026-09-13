from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FIGURE_DIR = PROJECT_ROOT / "figures"

# Create figures folder if it does not exist
FIGURE_DIR.mkdir(exist_ok=True)

api_file = DATA_DIR / "aei_raw_1p_api_2025-08-04_to_2025-08-11.csv"
claude_file = DATA_DIR / "aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv"

api = pd.read_csv(api_file)
claude = pd.read_csv(claude_file)

# --------------------------------------------------
# Helper function: get global collaboration data
# --------------------------------------------------

def get_global_collaboration(df, platform_name):

    result = df[
        (df["geo_id"] == "GLOBAL")
        & (df["facet"] == "collaboration")
        & (df["variable"] == "collaboration_pct")
    ][["cluster_name", "value"]].copy()

    result["platform"] = platform_name

    return result


api_collab = get_global_collaboration(api, "1P API")
claude_collab = get_global_collaboration(claude, "Claude.ai")

collaboration = pd.concat(
    [api_collab, claude_collab],
    ignore_index=True
)

# --------------------------------------------------
# Plot 1: Automation vs. Augmentation
# --------------------------------------------------

automation_categories = [
    "directive",
    "feedback loop",
]

augmentation_categories = [
    "learning",
    "task iteration",
    "validation",
]

summary_rows = []

for platform in ["1P API", "Claude.ai"]:

    platform_data = collaboration[
        collaboration["platform"] == platform
    ]

    automation = platform_data[
        platform_data["cluster_name"].isin(
            automation_categories
        )
    ]["value"].sum()

    augmentation = platform_data[
        platform_data["cluster_name"].isin(
            augmentation_categories
        )
    ]["value"].sum()

    summary_rows.append(
        {
            "platform": platform,
            "Automation": automation,
            "Augmentation": augmentation,
        }
    )

summary = pd.DataFrame(summary_rows)

print("\nAutomation and Augmentation Summary:")
print(summary.to_string(index=False))

plot1_data = summary.set_index("platform")

ax = plot1_data.plot(
    kind="bar",
    figsize=(8, 5)
)

ax.set_title("Automation vs. Augmentation by Platform")
ax.set_xlabel("Platform")
ax.set_ylabel("Percentage of Usage")
ax.set_ylim(0, 100)
ax.tick_params(axis="x", rotation=0)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "automation_vs_augmentation.png",
    dpi=300
)

plt.close()

# --------------------------------------------------
# Plot 2: Collaboration styles
# --------------------------------------------------

plot2_data = collaboration[
    collaboration["cluster_name"].isin(
        [
            "directive",
            "feedback loop",
            "learning",
            "task iteration",
            "validation",
        ]
    )
]

pivot_collab = plot2_data.pivot(
    index="cluster_name",
    columns="platform",
    values="value"
)

ax = pivot_collab.plot(
    kind="bar",
    figsize=(9, 5)
)

ax.set_title("Collaboration Styles by Platform")
ax.set_xlabel("Collaboration Style")
ax.set_ylabel("Percentage of Usage")
ax.tick_params(axis="x", rotation=30)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "collaboration_styles.png",
    dpi=300
)

plt.close()

# --------------------------------------------------
# Helper function: top O*NET tasks
# --------------------------------------------------

def get_top_tasks(df, platform_name, n=8):

    tasks = df[
        (df["geo_id"] == "GLOBAL")
        & (df["facet"] == "onet_task")
        & (df["variable"] == "onet_task_pct")
        & (~df["cluster_name"].isin(
            ["none", "not_classified"]
        ))
    ][["cluster_name", "value"]].copy()

    tasks = tasks.sort_values(
        "value",
        ascending=False
    ).head(n)

    tasks["platform"] = platform_name

    return tasks
# --------------------------------------------------
# Helper function: shorten long task labels for plots
# --------------------------------------------------

def shorten_label(text, max_length=55):

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."

# --------------------------------------------------
# Plot 3A: Top API O*NET tasks
# --------------------------------------------------

api_tasks = get_top_tasks(api, "1P API")

api_tasks_plot = api_tasks.sort_values(
    "value",
    ascending=True
).copy()

api_tasks_plot["short_label"] = (
    api_tasks_plot["cluster_name"].apply(shorten_label)
)

plt.figure(figsize=(9, 6))

plt.barh(
    api_tasks_plot["short_label"],
    api_tasks_plot["value"]
)

plt.title("Top O*NET Tasks — 1P API")
plt.xlabel("Percentage of Usage")
plt.ylabel("O*NET Task")

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "top_api_tasks.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# --------------------------------------------------
# Plot 3B: Top Claude.ai O*NET tasks
# --------------------------------------------------

claude_tasks = get_top_tasks(
    claude,
    "Claude.ai"
)

claude_tasks_plot = claude_tasks.sort_values(
    "value",
    ascending=True
).copy()

claude_tasks_plot["short_label"] = (
    claude_tasks_plot["cluster_name"].apply(shorten_label)
)

plt.figure(figsize=(9, 6))

plt.barh(
    claude_tasks_plot["short_label"],
    claude_tasks_plot["value"]
)

plt.title("Top O*NET Tasks — Claude.ai")
plt.xlabel("Percentage of Usage")
plt.ylabel("O*NET Task")

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "top_claude_tasks.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()