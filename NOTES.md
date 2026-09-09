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