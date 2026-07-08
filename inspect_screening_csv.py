import pandas as pd

df = pd.read_csv("openalex_genai_translanguaging_prompt_TAM_WTC_screening.csv")

print(df.columns)
print(df.head())
print(len(df))

