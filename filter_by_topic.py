import pandas as pd
import re
import sys

# ── 在这里定义你所有的主题过滤方案 ──────────────────────────
TOPICS = {
    "prompt_translanguaging_efl": {
        "description": "Prompt literacy + translanguaging + EFL writing",
        "must_match_any": [
            ["prompt literacy", "prompt engineering", "prompting", "chatgpt", "generative ai", "llm"],
            ["translanguaging", "multilingual", "bilingual", "efl", "esl", "l2 writing"],
        ],
        "exclude": [
            "stem", "medical", "clinical", "mathematics", "physics",
            "robotics", "autonomous driving",
        ],
    },
    "wtc_ai_writing": {
        "description": "WTC (Willingness to Communicate) + AI + writing",
        "must_match_any": [
            ["willingness to communicate", "wtc", "communication apprehension"],
            ["chatgpt", "generative ai", "llm", "ai-assisted", "ai feedback"],
            ["writing", "efl", "esl", "language learning"],
        ],
        "exclude": [
            "stem", "medical", "mathematics", "robotics",
        ],
    },
    "tam_ai_efl": {
        "description": "TAM (Technology Acceptance Model) + AI + EFL",
        "must_match_any": [
            ["technology acceptance model", "tam", "perceived usefulness", "behavioral intention"],
            ["chatgpt", "generative ai", "llm", "ai tool"],
            ["efl", "esl", "language learning", "writing"],
        ],
        "exclude": [
            "stem", "medical", "robotics",
        ],
    },
    "pretext_artefact_efl_writing": {
        "description": "Pre-text pedagogy + artefact + EFL writing",
        "must_match_any": [
            ["pre-text", "pretext", "artefact", "artifact", "multimodal", "drawing", "visual scaffold"],
            ["writing", "efl", "esl", "language learning", "composition"],
        ],
        "exclude": [
            "stem", "medical", "robotics",
        ],
    },
    "under13_ai_literacy": {
        "description": "Under-13 / primary school + AI literacy + writing",
        "must_match_any": [
            ["primary school", "elementary school", "k-12", "young learner", "under 13", "children"],
            ["ai literacy", "generative ai", "chatgpt", "llm", "prompt"],
            ["writing", "literacy", "language", "efl"],
        ],
        "exclude": [
            "mathematics", "science", "robotics", "medical",
        ],
    },
}

def filter_topic(df, topic_key):
    if topic_key not in TOPICS:
        print(f"Topic '{topic_key}' not found.")
        print(f"Available topics: {list(TOPICS.keys())}")
        return pd.DataFrame()

    config = TOPICS[topic_key]
    print(f"\nFiltering for: {config['description']}")

    # 清理 HTML 实体
    df = df.copy()
    df["title"] = df["title"].fillna("").str.replace("&apos;", "'").str.replace("&quot;", '"')
    text = (df["title"] + " " + df["abstract"].fillna("")).str.lower()

    # 排除
    mask_exclude = text.apply(
        lambda t: any(re.search(kw, t) for kw in config["exclude"])
    )

    # 每组 must_match_any 里至少命中一个
    masks_include = []
    for kw_group in config["must_match_any"]:
        mask = text.apply(lambda t: any(re.search(kw, t) for kw in kw_group))
        masks_include.append(mask)

    final_mask = ~mask_exclude
    for m in masks_include:
        final_mask = final_mask & m

    result = df[final_mask].copy()
    result["topic_filter"] = topic_key
    result["include_for_review"] = "candidate"
    result["screening_stage"] = "title_abstract"

    return result

# ── 主程序 ──────────────────────────────────────────────────
df = pd.read_csv("multi_source_preprints_v2.csv")

# 用法 1：指定单个主题
# python3 filter_by_topic.py prompt_translanguaging_efl

# 用法 2：不带参数 = 跑所有主题
if len(sys.argv) > 1:
    topics_to_run = [sys.argv[1]]
else:
    topics_to_run = list(TOPICS.keys())

for topic_key in topics_to_run:
    result = filter_topic(df, topic_key)
    if len(result) == 0:
        print(f"  No results for {topic_key}")
        continue

    output = f"candidates_{topic_key}.csv"
    result.to_csv(output, index=False, encoding="utf-8-sig")

    print(f"  Found {len(result)} candidates → {output}")
    print(f"  Source: {result['source'].value_counts().to_dict()}")
    print(f"  Titles:")
    for _, row in result.iterrows():
        print(f"    [{row['source']}][{row['publication_year']}] {str(row['title'])[:75]}")
