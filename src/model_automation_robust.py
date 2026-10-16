from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

INPUT_FILE = OUTPUT_DIR / "balanced_task_panel_min100.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("ROBUST AUTOMATION MODEL")
print("=" * 80)

df = pd.read_csv(INPUT_FILE)

print(f"\nRows: {len(df):,}")
print(f"Unique tasks: {df['task'].nunique():,}")


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "task",
    "platform",
    "period",
    "total_count",
    "automation_count",
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# BASIC COUNT CHECKS
# ============================================================

if (df["automation_count"] < 0).any():
    raise ValueError("Negative automation counts found.")

if (df["total_count"] <= 0).any():
    raise ValueError("Non-positive total counts found.")

if (
    df["automation_count"] > df["total_count"]
).any():
    raise ValueError(
        "Automation count exceeds total count."
    )

df["nonautomation_count"] = (
    df["total_count"]
    - df["automation_count"]
)

df["automation_prop"] = (
    df["automation_count"]
    / df["total_count"]
)

print("\nCount checks passed.")


# ============================================================
# SET REFERENCE CATEGORIES
# ============================================================

df["platform"] = pd.Categorical(
    df["platform"],
    categories=[
        "Claude.ai",
        "API",
    ],
    ordered=True,
)

df["period"] = pd.Categorical(
    df["period"],
    categories=[
        "Aug 2025",
        "Nov 2025",
        "Feb 2026",
    ],
    ordered=True,
)


# ============================================================
# MODEL FORMULA
# ============================================================

formula = (
    "automation_prop ~ "
    "C(platform) * C(period) + C(task)"
)


# ============================================================
# FIT ORIGINAL BINOMIAL MODEL
# ============================================================

print("\nFitting original binomial GLM...")

model = smf.glm(
    formula=formula,
    data=df,
    family=sm.families.Binomial(),
    freq_weights=df["total_count"],
)

result = model.fit()

print("Original model finished.")


# ============================================================
# OVERDISPERSION DIAGNOSTIC
# ============================================================

pearson_chi2 = result.pearson_chi2
deviance = result.deviance
df_resid = result.df_resid

pearson_dispersion = (
    pearson_chi2 / df_resid
)

deviance_dispersion = (
    deviance / df_resid
)

print("\n" + "=" * 80)
print("OVERDISPERSION DIAGNOSTIC")
print("=" * 80)

print(
    f"Pearson chi-square: "
    f"{pearson_chi2:,.2f}"
)

print(
    f"Deviance: "
    f"{deviance:,.2f}"
)

print(
    f"Residual df: "
    f"{df_resid:,.2f}"
)

print(
    f"Pearson dispersion ratio: "
    f"{pearson_dispersion:.4f}"
)

print(
    f"Deviance dispersion ratio: "
    f"{deviance_dispersion:.4f}"
)

print(
    "\nNOTE: With frequency weights, the model's "
    "residual degrees of freedom reflect the "
    "expanded aggregate counts. These ratios "
    "should therefore be interpreted cautiously."
)


# ============================================================
# FIT CLUSTER-ROBUST VERSION
# ============================================================
#
# The coefficient estimates remain the same.
# We change how uncertainty is estimated.
#
# Observations belonging to the same task are treated
# as a cluster because each task appears repeatedly
# across platforms and periods.
#
# ============================================================

print("\n" + "=" * 80)
print("FITTING TASK-CLUSTERED MODEL")
print("=" * 80)

print(
    "\nClustering standard errors by task..."
)

try:

    robust_result = model.fit(
        cov_type="cluster",
        cov_kwds={
            "groups": df["task"],
            "use_correction": True,
        },
    )

    robust_method = "Task-clustered standard errors"

    print("Clustered model finished.")

except Exception as error:

    print("\nWARNING:")
    print(
        "statsmodels could not calculate clustered "
        "standard errors for this weighted GLM."
    )

    print("\nError message:")
    print(error)

    print(
        "\nFalling back to Pearson-scale adjusted "
        "standard errors."
    )

    robust_result = model.fit(
        scale="X2"
    )

    robust_method = (
        "Pearson-scale adjusted standard errors"
    )


# ============================================================
# BUILD COEFFICIENT TABLE
# ============================================================

robust_table = pd.DataFrame(
    {
        "coefficient": robust_result.params,
        "std_error": robust_result.bse,
        "z_value": robust_result.tvalues,
        "p_value": robust_result.pvalues,
    }
)

robust_table["odds_ratio"] = np.exp(
    robust_table["coefficient"]
)

robust_table["ci_lower"] = (
    robust_table["coefficient"]
    - 1.96 * robust_table["std_error"]
)

robust_table["ci_upper"] = (
    robust_table["coefficient"]
    + 1.96 * robust_table["std_error"]
)

robust_table["odds_ratio_ci_lower"] = np.exp(
    robust_table["ci_lower"]
)

robust_table["odds_ratio_ci_upper"] = np.exp(
    robust_table["ci_upper"]
)


# ============================================================
# SELECT ONLY PLATFORM/PERIOD TERMS
# ============================================================
#
# We explicitly name the terms here.
# This fixes the earlier printing bug where a task
# description containing the word "period" appeared.
#
# ============================================================

terms_to_report = [
    "C(platform)[T.API]",
    "C(period)[T.Nov 2025]",
    "C(period)[T.Feb 2026]",
    (
        "C(platform)[T.API]:"
        "C(period)[T.Nov 2025]"
    ),
    (
        "C(platform)[T.API]:"
        "C(period)[T.Feb 2026]"
    ),
]

existing_terms = [
    term for term in terms_to_report
    if term in robust_table.index
]

main_results = robust_table.loc[
    existing_terms
].copy()


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 80)
print("ROBUST PLATFORM AND PERIOD RESULTS")
print("=" * 80)

print(f"\nMethod: {robust_method}\n")

print(
    main_results[
        [
            "coefficient",
            "std_error",
            "z_value",
            "p_value",
            "odds_ratio",
            "odds_ratio_ci_lower",
            "odds_ratio_ci_upper",
        ]
    ].to_string()
)


# ============================================================
# COMPARE ORIGINAL VS ROBUST STANDARD ERRORS
# ============================================================

comparison = pd.DataFrame(
    {
        "coefficient": result.params[
            existing_terms
        ],
        "original_se": result.bse[
            existing_terms
        ],
        "robust_se": robust_result.bse[
            existing_terms
        ],
        "original_p": result.pvalues[
            existing_terms
        ],
        "robust_p": robust_result.pvalues[
            existing_terms
        ],
    }
)

comparison["se_increase_factor"] = (
    comparison["robust_se"]
    / comparison["original_se"]
)


print("\n" + "=" * 80)
print("ORIGINAL VS ROBUST")
print("=" * 80)

print(
    comparison.to_string()
)


# ============================================================
# FOCUS ON INTERACTION TERMS
# ============================================================

interaction_terms = [
    (
        "C(platform)[T.API]:"
        "C(period)[T.Nov 2025]"
    ),
    (
        "C(platform)[T.API]:"
        "C(period)[T.Feb 2026]"
    ),
]

interaction_terms = [
    term for term in interaction_terms
    if term in robust_table.index
]

print("\n" + "=" * 80)
print("INTERACTION RESULTS")
print("=" * 80)

for term in interaction_terms:

    row = robust_table.loc[term]

    if "Nov 2025" in term:
        label = "API x November 2025"

    elif "Feb 2026" in term:
        label = "API x February 2026"

    else:
        label = term

    print(f"\n{label}")

    print(
        f"Coefficient: "
        f"{row['coefficient']:.6f}"
    )

    print(
        f"Robust SE: "
        f"{row['std_error']:.6f}"
    )

    print(
        f"z-value: "
        f"{row['z_value']:.3f}"
    )

    print(
        f"p-value: "
        f"{row['p_value']:.6g}"
    )

    print(
        f"Odds ratio: "
        f"{row['odds_ratio']:.4f}"
    )

    print(
        "95% OR CI: "
        f"[{row['odds_ratio_ci_lower']:.4f}, "
        f"{row['odds_ratio_ci_upper']:.4f}]"
    )


# ============================================================
# SAVE OUTPUTS
# ============================================================

robust_table.to_csv(
    OUTPUT_DIR /
    "automation_model_robust_coefficients.csv"
)

main_results.to_csv(
    OUTPUT_DIR /
    "automation_model_robust_main_terms.csv"
)

comparison.to_csv(
    OUTPUT_DIR /
    "automation_model_se_comparison.csv"
)

with open(
    OUTPUT_DIR /
    "automation_model_robust_summary.txt",
    "w",
) as file:

    file.write(
        robust_result.summary().as_text()
    )

print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print(
    "outputs/automation_model_robust_coefficients.csv"
)

print(
    "outputs/automation_model_robust_main_terms.csv"
)

print(
    "outputs/automation_model_se_comparison.csv"
)

print(
    "outputs/automation_model_robust_summary.txt"
)

print("\nDone!")