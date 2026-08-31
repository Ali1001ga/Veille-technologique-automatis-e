import pandas as pd
import re

CATEGORIES = {
    "Cloud": ["aws", "azure", "gcp", "cloud", "serverless"],
    "Data": ["pandas", "sql", "data engineer", "etl", "python", "analytics", "warehouse", "spark"],
    "DevOps": ["docker", "kubernetes", "ci/cd", "devops", "terraform", "pipeline"],
    "AI": ["ai", "machine learning", "llm", "gpt", "neural", "nlp", "ml model", "language model"]
}

def find_categories(text):
    text = str(text).lower()
    matches = []
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                matches.append(category)
                break
    return matches

def tag_dataframe(df, text_columns):
    df["text_to_check"] = df[text_columns].fillna("").agg(" ".join, axis=1)
    df["categories"] = df["text_to_check"].apply(find_categories)
    return df

blogs = pd.read_csv("blog_posts.csv")
blogs = tag_dataframe(blogs, ["title", "summary"])
blogs.to_csv("blog_posts_tagged.csv", index=False)

jobs = pd.read_csv("indeed_jobs.csv")
jobs = tag_dataframe(jobs, ["title"])
jobs.to_csv("indeed_jobs_tagged.csv", index=False)

print(blogs[["title", "categories"]].head())
print(jobs[["title", "categories"]].head())


linkedin_jobs = pd.read_csv("linkedin_jobs.csv")
linkedin_jobs = tag_dataframe(linkedin_jobs, ["title"])
linkedin_jobs.to_csv("linkedin_jobs_tagged.csv", index=False)
print(linkedin_jobs[["title", "categories"]].head())