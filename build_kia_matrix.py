#!/usr/bin/env python3
"""
build_kia_matrix.py

Generates a pre-filled KIA+Method matrix CSV from the merged core candidates.
Pre-populates known metadata and leaves KIA columns blank for manual annotation.

Usage:
    python build_kia_matrix.py \
        --input merged_candidates.csv \
        --output kia_matrix_draft.csv

KIA columns (to be filled manually after full-text reading):
    - K_gap          : Knowledge gap addressed
    - I_contribution : Intellectual contribution / main finding
    - A_implications : Applications / pedagogical implications
    - methodology    : Research design (qualitative/quantitative/mixed)
    - participants   : Who the study involves (age, context)
    - theoretical_framework : Key theory / model underpinning the study
    - AI_tool_used   : Specific GenAI/LLM tool if named
    - translanguaging_explicit : Yes/No/Partial
    - prompt_literacy_explicit : Yes/No/Partial
    - under13_context : Yes/No/Not specified
    - WTC_dimension  : Speaking/Writing/Digital/Not applicable
    - notes          : Free-text annotation
"""

import argparse
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# KIA column definitions (blank by default)
# ---------------------------------------------------------------------------
KIA_COLUMNS = [
    "K_gap",
    "I_contribution",
    "A_implications",
    "methodology",
    "participants",
    "theoretical_framework",
    "AI_tool_used",
    "translanguaging_explicit",
    "prompt_literacy_explicit",
    "under13_context",
    "WTC_dimension",
    "notes",
]

# ---------------------------------------------------------------------------
# Columns to carry over from the merged candidates CSV
# ---------------------------------------------------------------------------
SOURCE_COLUMNS = [
    "title",
    "authors",
    "year",
    "source",          # journal / conference / preprint server
    "doi",
    "abstract",
    "url",
    "relevance_tag",   # include / maybe / exclude
    "topic_flags",     # comma-separated matched themes
]


def build_matrix(input_path: str, output_path: str, include_maybe: bool = True) -> None:
    df = pd.read_csv(input_path)

    # Normalise column names to lowercase
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Filter to include / maybe only
    if "relevance_tag" in df.columns:
        keep_tags = ["include", "maybe"] if include_maybe else ["include"]
        df = df[df["relevance_tag"].str.lower().isin(keep_tags)].copy()
        print(f"[filter] Kept {len(df)} rows (tags: {keep_tags})")
    else:
        print("[warn] No 'relevance_tag' column found — keeping all rows.")

    # Keep only available source columns (gracefully skip missing ones)
    present_source = [c for c in SOURCE_COLUMNS if c in df.columns]
    missing_source = [c for c in SOURCE_COLUMNS if c not in df.columns]
    if missing_source:
        print(f"[warn] Missing source columns (will be blank): {missing_source}")

    out = df[present_source].copy()

    # Add any missing source columns as blank
    for col in missing_source:
        out[col] = ""

    # Reorder to SOURCE_COLUMNS order
    out = out[SOURCE_COLUMNS]

    # Append blank KIA columns
    for col in KIA_COLUMNS:
        out[col] = ""

    # Sort by year descending, then title
    if "year" in out.columns:
        out["year"] = pd.to_numeric(out["year"], errors="coerce")
        out = out.sort_values(["year", "title"], ascending=[False, True])

    out.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[done] KIA matrix saved to: {output_path}")
    print(f"       Rows: {len(out)} | KIA columns added: {len(KIA_COLUMNS)}")
    print("\nNext step: open kia_matrix_draft.csv in Excel / LibreOffice and")
    print("           fill in K_gap, I_contribution, A_implications, methodology,")
    print("           participants, theoretical_framework for each article.")


def main():
    parser = argparse.ArgumentParser(description="Build KIA+Method matrix from candidates CSV.")
    parser.add_argument("--input", default="merged_candidates.csv",
                        help="Path to merged candidates CSV (default: merged_candidates.csv)")
    parser.add_argument("--output", default="kia_matrix_draft.csv",
                        help="Output path for KIA matrix CSV (default: kia_matrix_draft.csv)")
    parser.add_argument("--include-maybe", action="store_true", default=True,
                        help="Include rows tagged 'maybe' (default: True)")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"[error] Input file not found: {args.input}")
        print("        Run fetch_multi_source_v2.py and filter_multi_source.py first.")
        return

    build_matrix(args.input, args.output, args.include_maybe)


if __name__ == "__main__":
    main()
