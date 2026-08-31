import feedparser

FEEDS = {
    "devto": "https://dev.to/feed",
    "medium": "https://medium.com/feed/tag/technology"
}

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
            "summary": entry.get("summary", "")
        })

print(len(posts))
print(posts[0])

import pandas as pd

df = pd.DataFrame(posts)
df.to_csv("blog_posts.csv", index=False)
