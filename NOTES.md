# Project Notes

## Step 2: Dataset Provenance

### Dataset
Anthropic Economic Index

### Release
September 15, 2025 release (`release_2025_09_15`)

### Primary Source
https://huggingface.co/datasets/Anthropic/EconomicIndex

### Release Source
https://huggingface.co/datasets/Anthropic/EconomicIndex/tree/main/release_2025_09_15

### Files Downloaded
- `aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv`
- `aei_raw_1p_api_2025-08-04_to_2025-08-11.csv`

### Download Date
September 7, 2026

### Data Collection Period
August 4, 2025 to August 11, 2025

### License
CC-BY for the released data.

### Why I Selected This Release
I selected the September 2025 release because it contains both Claude.ai
usage data and first-party API usage data. These two sources allow me to
compare how consumers and businesses use AI, which directly relates to my
research question.

### Research Question
Do enterprise API users exhibit more automation-oriented AI usage than
Claude.ai consumers, and does this difference vary across occupations and
over time?

### Citation
Appel, Ruth, Peter McCrory, Alex Tamkin, Michael Stern, Miles McCain,
and Tyler Neylon. "Anthropic Economic Index Report: Uneven Geographic
and Enterprise AI Adoption." Anthropic, September 15, 2025.

## Step 3: Dataset Documentation and Methodology

### How the Data Was Collected

The Anthropic Economic Index uses privacy-preserving methods to analyze
anonymized interactions with Claude. Anthropic uses its automated analysis
system, Clio, to classify interactions without researchers manually reading
individual conversations.

Claude interactions are mapped to work-related tasks from O*NET, which
contains thousands of work tasks associated with occupations.

For the September 2025 release, the project includes two main sources of
Claude usage:

1. Claude.ai usage: represents interactions through the consumer-facing
   Claude.ai product
2. First-party (1P) API usage: represents customers integrating Claude
   through Anthropic's API

The data collection period for the files used in this project is
August 4, 2025 through August 11, 2025.

### Unit of Observation

The released data and API data are aggregated rather than individual-level conversation
records.

For the Claude.ai dataset, each row represents one metric value for a
particular geography and analysis facet combination. Examples of facets
include O*NET task, collaboration pattern, request type, and intersections
between these categories.

### How Labels Were Produced

Anthropic uses automated privacy-preserving classification methods to map
Claude interactions to O*NET occupational tasks and other analysis
categories.

Human-AI collaboration patterns are classified into categories that
distinguish more automation-oriented interactions from more
augmentation-oriented interactions.

Automation refers to interactions where Claude performs or is delegated more
of the task. Augmentation refers to interactions where Claude assists the
human through patterns such as learning, validation, and task iteration.

These classifications allow the Economic Index to calculate automation and
augmentation percentages for different tasks and usage groups.

### Verification Targets

The following published findings will be used later to check whether my
processing and analysis are consistent with Anthropic's report:

1. Anthropic reports that approximately 77% of first-party API usage was
   automation-oriented.

2. Software development was the dominant category of first-party API usage.
   Among the 15 largest API use clusters, which together represented about
   half of API traffic, most were related to coding and software development.

3. Anthropic reports that debugging web applications and resolving technical
   issues each represented approximately 6% of API usage.

These published values will be compared with values calculated from the
downloaded data during the verification stage.

## Step 4: Dataset Inventory

The dataset inventory was generated using `src/inventory.py`. The script
examines each CSV file in the local `data/` directory and reports file size,
row count, column count, data types, and missing-value rates.

### File Inventory

| File | Size (MB) | Rows | Columns |
|---|---:|---:|---:|
| aei_raw_1p_api_2025-08-04_to_2025-08-11.csv | 6.70 | 33,794 | 10 |
| aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv | 18.02 | 100,062 | 10 |

### Columns and Data Types

Both datasets contain the same 10 fields:

| Column | Data Type |
|---|---|
| geo_id | string |
| geography | string |
| date_start | string |
| date_end | string |
| platform_and_product | string |
| facet | string |
| level | integer |
| variable | string |
| cluster_name | string |
| value | float |

### Missing Values

The first-party API dataset contained no missing values.

The Claude.ai dataset had a small amount of missing data:
- `cluster_name`: 0.4497% missing
- `geo_id`: 0.0220% missing
- All other fields: 0% missing

These values have not been removed.

### Claimed vs. Actual Verification

The inventory and verification checks were generated using
`src/inventory.py`.

Automation is defined as the sum of the `directive` and `feedback loop`
collaboration categories. Augmentation is defined as the sum of `learning`,
`task iteration`, and `validation`.

| Verification Target | Published / Expected | Calculated / Observed | Result |
|---|---|---|---|
| First-party API automation share | Approximately 77% | 77.37% | Verified |
| Claude.ai automation share | Approximately 50% | 49.10% | Consistent |
| Software development dominates API usage | Software development is the dominant category | Most of the largest classified O*NET task percentages are software, programming, debugging, web development, or other computing tasks | Supported |
| Specific API use clusters around 6% | Approximately 6% for selected use clusters discussed in the report | The O*NET task table does not contain an exact one-to-one match for these report-level clusters | Not directly reproduced from this table |

The first-party API automation result closely reproduces Anthropic's
published value. The Claude.ai data also show a substantially lower
automation share than the API data.

For this release, the difference in automation share is
28.27%.

Inspection of the API O*NET task distribution also supports the report's
broader finding that software development is a major source of API usage.
Several of the largest classified tasks involve modifying software, writing
programs, web development, machine learning, troubleshooting, debugging,
software testing, and related computing activities.

The approximately 6% report-level use-cluster findings were not directly
reproduced from the O*NET task table. 
Since the released O*NET tast categories do not appear
to correspond to one-to-one with report-level cluster descriptions, I recorded
the difference instead of treating unlike categories as equivalent.

During verification, I came across an important structural issue in collaboration percentages
in the Claude.ai file. These percentages pertained to many  
contains collaboration percentages for many geographic groups in addition to global records. 
Summing these geographic percentages produced invalid percentages greater than 100%. 
The verification calculation now uses only records where `geo_id` is `GLOBAL`.

## Step 5: Individual Record Inspection

The released Economic Index files contain aggregated metric records rather
than individual conversations. Therefore, the records inspected below
represent aggregate measurements for particular platforms, categories, and
time periods. Using `src/inspect_records.py`, six relevant records were chosen and inspected.

### Record 1: 1P API — Directive Collaboration

This record represents the global percentage of first-party API usage
classified as `directive` from August 4 through August 11, 2025. The value is
66.30%, indicating that directive interactions account for a large share of
API usage and helping explain the high overall automation percentage observed
during verification.

### Record 2: 1P API — Feedback Loop Collaboration

This record represents the global percentage of first-party API usage
classified as `feedback loop` during the same period. Its value is 11.08%.
Because feedback loop and directive interactions are both classified as
automation, this record combines with Record 1 to produce the approximately
77.37% API automation share.

### Record 3: 1P API — Largest Classified O*NET Task

The largest classified O*NET task in the global API data is modifying existing
software to correct errors, adapt it to new hardware, or improve its
performance. This task accounts for approximately 8.10% of API usage, which is
consistent with the broader finding that software-related work is prominent
in API usage.

### Record 4: Claude.ai — Directive Collaboration

This record represents the global percentage of Claude.ai Free and Pro usage
classified as `directive`. The value is approximately 38.78%, which is
substantially lower than the 66.30% directive share observed for the
first-party API. This difference is consistent with the initial descriptive
evidence that API usage is more automation-oriented.

### Record 5: Claude.ai — Task Iteration Collaboration

This record represents the global percentage of Claude.ai usage classified as
`task iteration`, which is an augmentation-oriented collaboration pattern. Its value is
approximately 22.22%, showing that a substantial portion of Claude.ai usage
involves iterative collaboration between the user and Claude rather than
direct task delegation.

### Record 6: Claude.ai — Largest Classified O*NET Task

The largest classified O*NET task in the global Claude.ai data is writing new
programs or modifying existing programs to meet customer requirements using
current programming languages and technologies. This task accounts for
approximately 4.87% of Claude.ai usage. Like the API result, this indicates
that software-related work is prominent, although the most common specific
task and its percentage differ between the two platforms.

