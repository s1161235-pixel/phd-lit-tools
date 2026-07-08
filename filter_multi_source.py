import pandas as pd
import re

df = pd.read_csv("multi_source_preprints_v2.csv")

# 清理 HTML 实体
df["title"] = df["title"].str.replace("&apos;", "'").str.replace("&quot;", '"').str.replace("&amp;", "&")

text = (df["title"].fillna("") + " " + df["abstract"].fillna("")).str.lower()

# 排除关键词
exclude_kw = [
    "stem education", "medical", "health care", "clinical",
    "mathematics", "physics", "chemistry", "coding",
    "software engineering", "computer science",
    "image generation", "video generation",
    "autonomous driving", "robotics",
]

# 纳入关键词组合（至少命中一个 prompt/AI 词 + 一个语言/写作词）
include_prompt = [
    "prompt literacy", "prompt engineering", "prompting",
    "generative ai", "chatgpt", "llm", "large language model",
    "ai-assisted", "ai feedback", "ai writing",
]
include_lang = [
    "translanguaging", "multilingual", "bilingual",
    "efl", "esl", "english language learner",
    "language learning", "writing instruction",
    "l2 writing", "second language writing",
    "plurilingual",
]

mask_exclude = text.apply(
    lambda t: any(re.search(kw, t) for kw in exclude_kw)
)
mask_prompt = text.apply(
    lambda t: any(re.search(kw, t) for kw in include_prompt)
)
mask_lang = text.apply(
    lambda t: any(re.search(kw, t) for kw in include_lang)
)

df_filtered = df[~mask_exclude & mask_prompt & mask_lang].copy()
df_filtered["include_for_review"] = "candidate"
df_filtered["screening_stage"] = "title_abstract"

df_filtered.to_csv(
    "multi_source_candidates.csv",
    index=False,
    encoding="utf-8-sig"
)

print(f"原始：{len(df)} 篇")
print(f"过滤后：{len(df_filtered)} 篇候选")
print(f"\n来源分布：")
print(df_filtered["source"].value_counts())
print(f"\n候选文章标题：")
for _, row in df_filtered.iterrows():
    print(f"  [{row['source']}][{row['publication_year']}] {row['title'][:80]}")
