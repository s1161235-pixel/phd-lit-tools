import requests
import pandas as pd
import time

BASE_URL = "https://api.openalex.org/works"
EMAIL = "selenaliu0707@outlook.com"
PER_PAGE = 100
MAX_PAGES_PER_QUERY = 5

QUERIES = {
    "Q1_genai_translanguaging_writing": {
        "search": '("generative AI" OR "large language model" OR ChatGPT) AND translanguaging AND writing',
        "filter": "type:article,from_publication_date:2022-01-01",
    },
    "Q2_pretext_sommer_ai_writing": {
        "search": '(("pre-text" OR pretext) AND Sommer) AND writing AND (AI OR "artificial intelligence")',
        "filter": "type:article,from_publication_date:2016-01-01",
    },
    "Q3_wtc_tech_feedback_writing": {
        "search": '"willingness to communicate" AND (AI OR ChatGPT OR "automated feedback") AND writing',
        "filter": "type:article,from_publication_date:1981-01-01",
    },
    "Q4_prompt_literacy_language_writing": {
        "search": '("prompt engineering" OR "prompt literacy") AND language AND writing',
        "filter": "type:article,from_publication_date:2022-01-01",
    },
    "Q5_tam_genai_writing_language": {
        "search": '"technology acceptance model" AND (ChatGPT OR "generative AI") AND writing AND language',
        "filter": "type:article,from_publication_date:2022-01-01",
    },
}

all_records = []

for label, cfg in QUERIES.items():
    print(f"\nRunning {label} ...")

    cursor = "*"
    page_count = 0

    while cursor and page_count < MAX_PAGES_PER_QUERY:
        params = {
            "search": cfg["search"],
            "filter": cfg["filter"],
            "sort": "publication_date:desc",
            "per-page": PER_PAGE,
            "cursor": cursor,
            "mailto": EMAIL,
        }

        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        meta = data.get("meta", {})
        next_cursor = meta.get("next_cursor")

        print(f"  Page {page_count + 1}: fetched {len(results)} records")

        if not results:
            break

        for w in results:
            primary_location = w.get("primary_location") or {}
            source = primary_location.get("source") or {}
            open_access = w.get("open_access") or {}

            authors = []
            for a in w.get("authorships", []):
                author = a.get("author") or {}
                name = author.get("display_name")
                if name:
                    authors.append(name)

            abstract_text = None
            inverted_index = w.get("abstract_inverted_index")
            if inverted_index:
                word_positions = []
                for word, positions in inverted_index.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract_text = " ".join(word for _, word in word_positions)

            all_records.append({
                "query_label": label,
                "search_string": cfg["search"],
                "title": w.get("title"),
                "publication_year": w.get("publication_year"),
                "publication_date": w.get("publication_date"),
                "journal": source.get("display_name"),
                "source_id": source.get("id"),
                "doi": w.get("doi"),
                "openalex_id": w.get("id"),
                "is_oa": open_access.get("is_oa"),
                "cited_by_count": w.get("cited_by_count"),
                "type": w.get("type"),
                "language": w.get("language"),
                "authors": "; ".join(authors),
                "abstract": abstract_text,
                "wos_ssci_checked": "",
                "wos_ssci_status": "",
                "wos_q1_checked": "",
                "wos_q1_status": "",
                "scopus_checked": "",
                "scopus_quartile": "",
                "include_for_review": "",
                "screening_stage": "",
                "screening_notes": "",
                "kia_keywords": "",
                "kia_intro_focus": "",
                "kia_abstract_focus": "",
            })

        cursor = next_cursor
        page_count += 1
        time.sleep(1)

df = pd.DataFrame(all_records)

if not df.empty:
    df = df.drop_duplicates(subset=["openalex_id"]).sort_values(
        by=["publication_date", "cited_by_count"],
        ascending=[False, False]
    )

output_file = "openalex_genai_translanguaging_prompt_TAM_WTC_screening.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"\nSaved {len(df)} unique records to {output_file}")
