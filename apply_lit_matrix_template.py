import pandas as pd
import sys

"""
apply_lit_matrix_template.py
-----------------------------
Universal KIA + method matrix template applicator.
Usage: python3 apply_lit_matrix_template.py <your_csv_file.csv>

Adds the following columns (if not already present) to any literature CSV:
- Basic context: country_context, educational_level
- KIA: kia_keywords, kia_intro_focus, kia_abstract_focus, theoretical_frame, research_questions
- Methods: design, population, context, ai_type, procedure_summary
- Method analysis: method_strengths, method_limitations, bias_risks, evaluation_notes
- Framework link: relevance_to_research_scope
- Screening (if not present): include_for_review, screening_stage, screening_notes
- Data extraction: key_findings
"""

TEMPLATE_COLS = [
    # Basic context
    "country_context",
    "educational_level",
    # KIA
    "research_questions",
    "kia_keywords",
    "kia_intro_focus",
    "kia_abstract_focus",
    "theoretical_frame",
    # Methods
    "design",
    "population",
    "context",
    "ai_type",
    "procedure_summary",
    # Method analysis
    "method_strengths",
    "method_limitations",
    "bias_risks",
    "evaluation_notes",
    # Framework link
    "relevance_to_research_scope",
    # Screening
    "include_for_review",
    "screening_stage",
    "screening_notes",
    # Data extraction
    "key_findings",
]

def apply_template(fname):
    try:
        df = pd.read_csv(fname, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(fname, encoding="utf-8")

    added = []
    for col in TEMPLATE_COLS:
        if col not in df.columns:
            df[col] = ""
            added.append(col)

    df.to_csv(fname, index=False, encoding="utf-8-sig")

    print(f"\nTemplate applied to: {fname}")
    print(f"Total rows: {len(df)}")
    print(f"Total columns now: {len(df.columns)}")
    if added:
        print(f"\nNewly added columns ({len(added)}):")
        for c in added:
            print(f"  + {c}")
    else:
        print("\nAll template columns already present, no changes needed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 apply_lit_matrix_template.py sv_file>")
        print("Example: python3 apply_lit_matrix_template.py my_literature.csv")
        sys.exit(1)
    apply_template(sys.argv[1])
