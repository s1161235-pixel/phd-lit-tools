import requests
import pandas as pd
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote

SEARCH_TOPICS = {
    "translanguaging_genai_writing": {
        "arxiv": 'ti:"translanguaging" AND abs:"generative AI" OR ti:"translanguaging" AND abs:"large language model"',
        "eric": "translanguaging generative AI writing",
    },
    "prompt_literacy_efl": {
        "arxiv": 'ti:"prompt literacy" OR abs:"prompt literacy" AND abs:"EFL" OR abs:"multilingual"',
        "eric": "prompt literacy EFL multilingual writing",
    },
    "ai_literacy_multilingual_writing": {
        "arxiv": 'ti:"AI literacy" AND abs:"multilingual" OR ti:"AI literacy" AND abs:"writing"',
        "eric": "AI literacy multilingual writing instruction",
    },
    "primary_school_ai_writing": {
        "arxiv": 'ti:"primary school" AND abs:"language" AND abs:"AI" OR ti:"elementary" AND abs:"ChatGPT" AND abs:"writing"',
        "eric": "primary school ChatGPT writing EFL literacy",
    },
    "translanguaging_llm": {
        "arxiv": 'ti:"translanguaging" AND abs:"LLM" OR ti:"translanguaging" AND abs:"ChatGPT"',
        "eric": "translanguaging LLM ChatGPT language learning",
    },
    "prompt_engineering_efl": {
        "arxiv": 'ti:"prompt engineering" AND abs:"EFL" OR ti:"prompt engineering" AND abs:"language learning"',
        "eric": "prompt engineering EFL ESL writing instruction",
    },
}

all_records = []

# ════════════════════════════════════════
# 1. arXiv（精确字段搜索）
# ════════════════════════════════════════
print("\n" + "="*50)
print("SOURCE 1: arXiv (title + abstract search)")
print("="*50)

ARXIV_URL = "http://export.arxiv.org/api/query"

for label, queries in SEARCH_TOPICS.items():
    query = queries["arxiv"]
    print(f"\n  [{label}]")
    params = {
        "search_query": query,
        "start": 0,
        "max_results": 25,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    try:
        resp = requests.get(ARXIV_URL, params=params, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        print(f"  Found {len(entries)} results")

        for entry in entries:
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)
            arxiv_id = entry.find("atom:id", ns)
            authors = [
                a.find("atom:name", ns).text
                for a in entry.findall("atom:author", ns)
                if a.find("atom:name", ns) is not None
            ]
            pdf_url = None
            for link in entry.findall("atom:link", ns):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href")
                    break

            year = int(published.text[:4]) if published is not None else None

            all_records.append({
                "source": "arXiv",
                "query_label": label,
                "title": title.text.strip() if title is not None else None,
                "abstract": summary.text.strip() if summary is not None else None,
                "publication_date": published.text[:10] if published is not None else None,
                "publication_year": year,
                "authors": "; ".join(authors),
                "source_id": arxiv_id.text if arxiv_id is not None else None,
                "doi": None,
                "journal": "arXiv preprint",
                "is_oa": True,
                "pdf_url": pdf_url,
            })
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(3)

# ════════════════════════════════════════
# 2. ERIC
# ════════════════════════════════════════
print("\n" + "="*50)
print("SOURCE 2: ERIC")
print("="*50)

ERIC_URL = "https://api.ies.ed.gov/eric/"

for label, queries in SEARCH_TOPICS.items():
    query = queries["eric"]
    print(f"\n  [{label}]")
    params = {
        "search": query,
        "format": "json",
        "rows": 25,
        "start": 0,
        "fields": "title,author,publicationdateyear,description,url,id,source",
    }
    try:
        resp = requests.get(ERIC_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        docs = data.get("response", {}).get("docs", [])
        print(f"  Found {len(docs)} results")

        for doc in docs:
            eric_id = doc.get("id", "")
            title = doc.get("title", "")
            year = doc.get("publicationdateyear")
            # 修复：确保 year 是 int
            try:
                year = int(year) if year is not None else None
            except (ValueError, TypeError):
                year = None

            all_records.append({
                "source": "ERIC",
                "query_label": label,
                "title": title,
                "abstract": doc.get("description"),
                "publication_date": str(year) if year else None,
                "publication_year": year,
                "authors": "; ".join(doc.get("author", [])) if isinstance(doc.get("author"), list) else str(doc.get("author", "")),
                "source_id": eric_id,
                "doi": None,
                "journal": doc.get("source"),
                "is_oa": True if doc.get("url", "").endswith(".pdf") else None,
                "pdf_url": doc.get("url") if doc.get("url", "").endswith(".pdf") else None,
            })
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(2)

# ════════════════════════════════════════
# 整合 + 去重 + 过滤
# ════════════════════════════════════════
df = pd.DataFrame(all_records)

# 去重（按标题）
df = df.drop_duplicates(subset=["title"])

# 只保留 2022 年以后
df = df[df["publication_year"].apply(lambda x: x is not None and int(x) >= 2022)]
df = df.sort_values(by=["publication_year", "source"], ascending=[False, True])

# 加 KIA 空白列
for col in [
    "include_for_review", "screening_stage", "screening_notes",
    "kia_keywords", "kia_intro_focus", "kia_abstract_focus",
    "theoretical_frame", "design", "population", "context",
    "ai_type", "key_findings", "relevance_to_research_scope",
]:
    df[col] = ""

# ResearchGate + Academia 搜索链接
rg_links = []
for label, queries in SEARCH_TOPICS.items():
    q = queries["eric"]
    rg_links.append({
        "topic": label,
        "query": q,
        "researchgate_url": f"https://www.researchgate.net/search?q={quote(q)}",
        "academia_url": f"https://www.academia.edu/search?q={quote(q)}",
    })
df_links = pd.DataFrame(rg_links)

# 保存
output = "multi_source_preprints_v2.csv"
df.to_csv(output, index=False, encoding="utf-8-sig")
df_links.to_csv("search_links_rg_academia.csv", index=False, encoding="utf-8-sig")

print("\n" + "="*50)
print(f"总文献数：{len(df)} 篇 → {output}")
print(f"\n来源分布：")
print(df["source"].value_counts())
print(f"\n标题预览（前 20 篇）：")
for _, row in df.head(20).iterrows():
    print(f"  [{row['source']}][{row['publication_year']}] {str(row['title'])[:75]}")

