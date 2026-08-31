import pandas as pd
import sqlite3

conn = sqlite3.connect("veille.db")

pd.read_csv("trends_morocco.csv").to_sql("trends_morocco", conn, if_exists="replace", index=False)
pd.read_csv("trends_france.csv").to_sql("trends_france", conn, if_exists="replace", index=False)
pd.read_csv("blog_posts_tagged.csv").to_sql("blog_posts", conn, if_exists="replace", index=False)
pd.read_csv("indeed_jobs_tagged.csv").to_sql("indeed_jobs", conn, if_exists="replace", index=False)
pd.read_csv("linkedin_jobs_tagged.csv").to_sql("linkedin_jobs", conn, if_exists="replace", index=False)

conn.close()
print("Saved to veille.db")