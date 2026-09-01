import feedparser
import pandas as pd
from bs4 import BeautifulSoup

FEEDS = {
    "devto": "https://dev.to/feed",
    "devto_python": "https://dev.to/feed/tag/python",
    "devto_docker": "https://dev.to/feed/tag/docker",
    "devto_cloud": "https://dev.to/feed/tag/cloud",
    "devto_ai": "https://dev.to/feed/tag/ai",
    "medium": "https://medium.com/feed/tag/technology",
    "medium_cloud": "https://medium.com/feed/tag/cloud-computing",
    "medium_ai": "https://medium.com/feed/tag/artificial-intelligence",
    "infoq": "https://feed.infoq.com/RSS/articles/"
}

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)

posts = []

for source, url in FEEDS.items():
    feed = feedparser.parse(url)
    print(source, len(feed.entries))
    for entry in feed.entries:
        posts.append({
            "source": source,
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", ""),
            "summary": clean_html(entry.get("summary", ""))
        })

df = pd.DataFrame(posts)
df = df.drop_duplicates(subset="title")
df.to_csv("blog_posts.csv", index=False)
print(f"Saved {len(df)} unique posts")