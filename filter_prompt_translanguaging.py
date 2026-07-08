import pandas as pd

df = pd.read_csv("openalex_genai_translanguaging_prompt_TAM_WTC_screening.csv")

mask_query = df["query_label"].isin([
    "Q1_genai_translanguaging_writing",
    "Q4_prompt_literacy_language_writing"
])

text = (df["title"].fillna("") + " " + df["abstract"].fillna("")).str.lower()

keywords_prompt = ["prompt", "prompting", "prompt literacy", "prompt engineering"]
keywords_trans = ["translanguaging", "multilingual", "bilingual", "cross-linguistic", "biliteracy"]

mask_prompt = text.str.contains("|".join(keywords_prompt))
mask_trans = text.str.contains("|".join(keywords_trans))

df_theme = df[mask_query & mask_prompt & mask_trans]

print(len(df_theme))
df_theme.to_csv("theme_prompt_translanguaging_efl_candidates.csv",
                index=False, encoding="utf-8-sig")
