import pandas as pd

df_theme = pd.read_csv("theme_prompt_translanguaging_efl_candidates.csv")

print("Rows:", len(df_theme))
print("\nColumns:")
print(df_theme.columns)

print("\nQuery label counts:")
print(df_theme["query_label"].value_counts())

print("\nSample titles:")
print(df_theme[["query_label", "title", "journal", "publication_year"]].head(12))

