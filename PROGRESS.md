# Capstone Progress Log

## Week of September 7 - 14

> [!NOTE]
> **Progress**
> - Set up the capstone GitHub repository and project structure.
> - Created the project README and documented the research question.
> - Selected the June 26, 2026 Anthropic Economic Index release.
> - Documented the dataset source, release information, license, and citation.
> - Reviewed the dataset documentation and research paper.
> - Documented how the data was collected, the unit of observation, and important dataset labels.
> - Created `src/inventory.py` to examine the datasets.
> - Compared the documented dataset structure with the actual downloaded files.
> - Examined sample records from the Claude.ai and API datasets.
> - Created `src/profile.py` and performed the initial exploratory analysis.
> - Created figures comparing automation and augmentation usage between Claude.ai and API.
> - Documented the initial findings in `PROFILE.md`.

> [!IMPORTANT]
> **Initial Finding**
> - Claude.ai usage appeared relatively balanced between automation and augmentation.
> - API usage appeared substantially more automation-oriented.

> [!WARNING]
> **Limitation Identified**
> - The initial analysis does not yet compare identical O*NET tasks between Claude.ai and API.

---

## Week of September 14 - 21

> [!NOTE]
> **Progress**
> - Conducted task-level analysis of the Claude.ai and API datasets.
> - Examined how O*NET tasks were represented in the data.
> - Compared task availability between Claude.ai and API.
> - Began restricting the analysis to tasks that could be compared across both platforms.
> - Shifted the analysis from overall automation averages toward an apples-to-apples task comparison.

> [!IMPORTANT]
> **Initial Finding**
> - The set of tasks represented in Claude.ai and API usage was not identical.
> - Comparing matched tasks was necessary so that differences in automation were less likely to be caused only by differences in task composition.

> [!WARNING]
> **Limitation Identified**
> - Task matching within a single release did not answer how the API–Claude.ai difference changed over time.
> - Additional releases were needed to create a longitudinal comparison.

--- 

## Week of September 21 - October 4

> [!NOTE]
> **Progress**
> - Expanded the project from a single-release comparison to a multi-release analysis.
> - Worked on constructing a task panel so that the same types of tasks could be followed across releases.
> - Added January 2026 and March 2026 data to the analysis.
> - Conducted sensitivity and compatibility checks across releases.
> - Evaluated whether the June 2026 release could be included with the earlier releases.
> - Refined the research question to focus on how the API–Claude.ai automation gap changes over time for comparable tasks.

> [!IMPORTANT]
> **Initial Finding**
> - September 2025, January 2026, and March 2026 could be used together for the longitudinal task comparison.
> - Sensitivity testing indicated that the June 2026 release did not align sufficiently with the earlier releases for the same primary analysis.
> - This supported using the three earlier compatible releases for a more consistent longitudinal comparison.

> [!WARNING]
> **Limitation Identified**
> - The analysis still needed a consistent matched-task panel across both platforms and all three releases.
> - The longitudinal results were still descriptive and had not yet been evaluated statistically.

--- 

## Week of October 12 - 19

> [!NOTE]
> **Progress**
> - Combined our individual capstone work into one shared team repository.
> - Updated the project direction and research question for the team analysis.
> - Conducted a longitudinal automation-gap analysis using September 2025, January 2026, and March 2026.
> - Constructed a balanced panel of **904 O*NET tasks** that were available for both Claude.ai and API across all three releases.
> - Calculated automation percentages for Claude.ai and API for the matched tasks.
> - Calculated the task-level automation gap as: **Automation Gap = API Automation % - Claude.ai Automation %**
> - Created longitudinal figures showing:
>   - Automation by source over time
>   - The average automation gap over time
>   - The distribution of matched-task automation gaps
>   - Tasks with the largest changes in the automation gap
> - Began updating `README.md`, `PROFILE.md`, and the project figures so that the repository reflects the new longitudinal research question.

> [!IMPORTANT]
> **Initial Finding**
> - API usage remained substantially more automation-oriented than Claude.ai usage across all three releases.
> - The average automation gap was approximately:
>   - **37.89 percentage points** in September 2025
>   - **41.92 percentage points** in January 2026
>   - **38.76 percentage points** in March 2026
> - The automation gap increased from September to January and then decreased again by March.
> - This suggests that the API–Claude.ai difference fluctuated over time rather than following a simple increasing or decreasing trend.

> [!WARNING]
> **Limitation Identified**
> - The current longitudinal analysis is descriptive and does not yet test whether the changes in the automation gap are statistically significant.
> - The June 2026 release was considered but was excluded from the primary longitudinal analysis because sensitivity testing showed that it was not sufficiently comparable with the earlier releases.

### Next Step
- Investigate what kinds of tasks are driving the automation gap over time.
- Determine which tasks experienced the largest increases or decreases in the API–Claude.ai gap.

---

## Week of October 19 - 26

> [!NOTE]
> **Progress**
> - Developed a clear, testable research hypothesis.
> - Added the hypothesis to the project's README.md.
> - Completed a decomposition analysis to investigate what contributed to the change in the automation gap between API and Claude.ai.
> - Compared changes in automation rates across the same 352 tasks from August 2025 to February 2026.

> [!IMPORTANT]
> **Hypothesis**
> - Our hypothesis is that the difference in automation-oriented AI usage between API and Claude.ai will decrease over time when comparing the same tasks.

> [!IMPORTANT]
> **Initial Finding**
> - The automation gap narrowed by approximately 4.8 percentage points from August 2025 to February 2026.
> - API automation decreased by 7.19 percentage points, while Claude.ai automation decreased by 2.38 percentage points, suggesting the narrowing was primarily driven by the larger decrease on the API side.
> - Approximately 63% of the matched tasks experienced a narrowing gap.

> [!WARNING]
> **Limitation Identified**
> - The hypothesis was developed after our initial exploratory analysis, so the existing results should be treated as exploratory rather than an independent confirmation.
> - The aggregated data cannot explain the underlying reasons for changes in automation behavior.

### Next Step
- Examine the O*NET task hierarchy to determine how tasks can be reliably mapped to occupations.
- Investigate whether automation gap changes differ across occupations or task categories.
- Continue evaluating the hypothesis through additional analyses and robustness checks.

---