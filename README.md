# phd-lit-tools

A reusable Python pipeline for OpenAlex literature retrieval, thematic filtering, and KIA+method matrix template generation — built for PhD research in applied linguistics and AI literacy education.

## Research Scope

This pipeline supports a systematic literature review focused on:
- **GenAI / LLM prompt literacy** in L2/EFL writing contexts
- **Translanguaging** as pedagogy in AI-mediated writing tasks
- **Under-13 learners** in constrained / teacher-mediated AI environments
- **Willingness to Communicate (WTC)** — including written, digital, and AI-mediated dimensions
- **Technology Acceptance Model (TAM)** applied to GenAI tools in language education

## Pipeline Overview

```
Fetch  →  Filter  →  Merge  →  Build KIA Matrix  →  Manual Annotation  →  SOLVE Synthesis
```

## Scripts

### 1. `fetch_openalex_multiqueries.py`
Fetches literature from **OpenAlex** using multiple thematic query strings.
```bash
python fetch_openalex_multiqueries.py
# Output: openalex_results.csv
```

### 2. `fetch_multi_source_v2.py`
Fetches from **OpenAlex + arXiv + ERIC** in parallel with configurable queries.
```bash
python fetch_multi_source_v2.py
# Output: multi_source_raw.csv
```

### 3. `filter_prompt_translanguaging.py`
Filters OpenAlex results for prompt literacy + translanguaging themes.
```bash
python filter_prompt_translanguaging.py
# Input:  openalex_results.csv
# Output: filtered_prompt_translanguaging.csv
```

### 4. `filter_by_topic.py`
General-purpose topic filter using configurable keyword sets.
```bash
python filter_by_topic.py --input multi_source_raw.csv --topic wtc_tam
# Output: filtered_<topic>.csv
```

### 5. `filter_multi_source.py`
Applies multi-theme filtering to the multi-source raw CSV and tags each row.
```bash
python filter_multi_source.py
# Input:  multi_source_raw.csv
# Output: merged_candidates.csv  (tagged include / maybe / exclude)
```

### 6. `apply_lit_matrix_template.py`
Applies the universal KIA+Method column template to any existing CSV.
```bash
python apply_lit_matrix_template.py --input filtered_prompt_translanguaging.csv
# Output: filtered_prompt_translanguaging_matrix.csv
```

### 7. `build_kia_matrix.py`  ← **Start here for annotation**
Generates a clean KIA+Method matrix CSV from the merged candidates, pre-populated with metadata and blank KIA columns ready for manual full-text annotation.
```bash
python build_kia_matrix.py \
    --input merged_candidates.csv \
    --output kia_matrix_draft.csv
```

**KIA columns added (fill manually after full-text reading):**

| Column | Description |
|---|---|
| `K_gap` | Knowledge gap the study addresses |
| `I_contribution` | Main intellectual contribution / finding |
| `A_implications` | Pedagogical / practical implications |
| `methodology` | Research design (qualitative / quantitative / mixed) |
| `participants` | Who the study involves (age, context, n=) |
| `theoretical_framework` | Key theory or model underpinning the study |
| `AI_tool_used` | Specific GenAI / LLM tool named (if any) |
| `translanguaging_explicit` | Yes / No / Partial |
| `prompt_literacy_explicit` | Yes / No / Partial |
| `under13_context` | Yes / No / Not specified |
| `WTC_dimension` | Speaking / Writing / Digital / Not applicable |
| `notes` | Free-text annotation |

### 8. `inspect_screening_csv.py`
Quick inspection tool for any screening CSV — prints summary stats.
```bash
python inspect_screening_csv.py --input kia_matrix_draft.csv
```

### 9. `inspect_theme_prompt_transla...py`
Inspects theme distribution in the prompt+translanguaging filtered output.

## Workflow

```bash
# Step 1: activate environment
source .venv/bin/activate

# Step 2: fetch from all sources
python fetch_multi_source_v2.py

# Step 3: filter and tag candidates
python filter_multi_source.py

# Step 4: build the KIA annotation matrix
python build_kia_matrix.py --input merged_candidates.csv --output kia_matrix_draft.csv

# Step 5: open kia_matrix_draft.csv in Excel / LibreOffice
# Fill in K_gap, I_contribution, A_implications, methodology,
# participants, theoretical_framework for each include/maybe article.
```

## Data Files (local only — not version-controlled)

| File | Description |
|---|---|
| `openalex_results.csv` | Raw OpenAlex fetch |
| `multi_source_raw.csv` | Raw multi-source fetch |
| `merged_candidates.csv` | Filtered + tagged candidates |
| `kia_matrix_draft.csv` | KIA matrix ready for annotation |

> **Note:** CSV data files are excluded from version control (see `.gitignore`). Only pipeline scripts are tracked here.

## Requirements

```bash
pip install pandas requests
```

## Citation Context

This pipeline was developed to support a PhD systematic literature review on:
> *GenAI prompt literacy, translanguaging, and EFL writing pedagogy — with a focus on under-13 learners in constrained AI environments.*
