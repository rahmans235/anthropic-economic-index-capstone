from pathlib import Path
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# --------------------------------------------------
# Project folders
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

PANEL_FILE = OUTPUT_DIR / "balanced_task_panel_min100.csv"

# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(PANEL_FILE)

print("=" * 80)
print("AUTOMATION MODEL")
print("=" * 80)

print(f"\nRows: {len(df):,}")
print(f"Unique tasks: {df['task'].nunique():,}")

print("\nPlatforms:")
print(df["platform"].value_counts())

print("\nPeriods:")
print(df["period"].value_counts())

# --------------------------------------------------
# Check counts
# --------------------------------------------------

# Non-automation observations
df["nonautomation_count"] = (
    df["total_count"] - df["automation_count"]
)

# Proportion automated
df["automation_prop"] = (
    df["automation_count"] / df["total_count"]
)

# Basic validity checks
if (df["automation_count"] < 0).any():
    raise ValueError("Negative automation counts found.")

if (df["nonautomation_count"] < 0).any():
    raise ValueError(
        "Automation count is larger than total count."
    )

if (df["total_count"] <= 0).any():
    raise ValueError("Non-positive total counts found.")

print("\nCount checks passed.")

# --------------------------------------------------
# Set category/reference order
# --------------------------------------------------

df["platform"] = pd.Categorical(
    df["platform"],
    categories=["Claude.ai", "API"],
    ordered=True
)

df["period"] = pd.Categorical(
    df["period"],
    categories=[
        "Aug 2025",
        "Nov 2025",
        "Feb 2026"
    ],
    ordered=True
)

# Claude.ai is the reference platform.
# August 2025 is the reference period.

# --------------------------------------------------
# Fit binomial GLM
# --------------------------------------------------
#
# Outcome:
# automation_count / total_count
#
# freq_weights tells the model how many observations
# contributed to each aggregate proportion.
#
# C(task) adds task fixed effects.
#
# platform * period expands to:
# platform
# + period
# + platform:period
# --------------------------------------------------

formula = (
    "automation_prop ~ "
    "C(platform) * C(period) + C(task)"
)

print("\nFitting model...")
print("This may take a little while because there are 352 task effects.")

model = smf.glm(
    formula=formula,
    data=df,
    family=sm.families.Binomial(),
    freq_weights=df["total_count"]
)

result = model.fit()

print("\nModel finished.")

# --------------------------------------------------
# Print only coefficients relevant to our
# main research question
# --------------------------------------------------

coefficients = pd.DataFrame(
    {
        "coefficient": result.params,
        "std_error": result.bse,
        "z_value": result.tvalues,
        "p_value": result.pvalues
    }
)

main_terms = coefficients[
    coefficients.index.str.contains(
        "platform|period",
        case=False,
        regex=True
    )
].copy()

print("\n" + "=" * 80)
print("PLATFORM AND PERIOD RESULTS")
print("=" * 80)

print(main_terms.to_string())

# --------------------------------------------------
# Model information
# --------------------------------------------------

print("\n" + "=" * 80)
print("MODEL INFORMATION")
print("=" * 80)

print(f"Number of rows: {len(df):,}")
print(f"Number of tasks: {df['task'].nunique():,}")
print(f"Total aggregate count: {df['total_count'].sum():,.0f}")

print(f"\nAIC: {result.aic:.2f}")
print(f"Deviance: {result.deviance:.2f}")
print(f"Pearson chi-square: {result.pearson_chi2:.2f}")

# --------------------------------------------------
# Save coefficients
# --------------------------------------------------

coefficients.to_csv(
    OUTPUT_DIR / "automation_model_coefficients.csv"
)

main_terms.to_csv(
    OUTPUT_DIR / "automation_model_main_terms.csv"
)

# Save complete text summary
with open(
    OUTPUT_DIR / "automation_model_summary.txt",
    "w"
) as f:
    f.write(result.summary().as_text())

print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print("outputs/automation_model_coefficients.csv")
print("outputs/automation_model_main_terms.csv")
print("outputs/automation_model_summary.txt")

print("\nDone!")