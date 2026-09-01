import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Veille Technologique IT/Data", page_icon="📊", layout="wide")

st.markdown("""
<style>
h1, h2, h3 { color: #4FD1C5; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Veille Technologique — Tendances IT/Data Maroc & France")

conn = sqlite3.connect("veille.db")
CATEGORIES = ["Cloud", "Data", "DevOps", "AI"]

blogs_df = pd.read_sql("SELECT * FROM blog_posts", conn)
jobs_df = pd.read_sql("SELECT * FROM indeed_jobs", conn)
linkedin_df = pd.read_sql("SELECT * FROM linkedin_jobs", conn)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Google Trends", "Blog Posts", "Indeed", "LinkedIn", "Indicateurs"])

with tab1:
    country = st.selectbox("Country", ["Morocco", "France"])
    table = "trends_morocco" if country == "Morocco" else "trends_france"
    trends_df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.line_chart(trends_df.set_index("date"))

with tab2:
    blog_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="blog_filter")
    blogs_display = blogs_df[blogs_df["categories"].str.contains(blog_filter, na=False)] if blog_filter != "All" else blogs_df
    st.metric("Total posts", len(blogs_display))
    st.dataframe(blogs_display[["source", "title", "categories"]], use_container_width=True)

with tab3:
    indeed_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="indeed_filter")
    jobs_display = jobs_df[jobs_df["categories"].str.contains(indeed_filter, na=False)] if indeed_filter != "All" else jobs_df
    st.metric("Total postings", len(jobs_display))
    st.dataframe(jobs_display[["title", "company", "location"]], use_container_width=True)

with tab4:
    linkedin_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="linkedin_filter")
    linkedin_display = linkedin_df[linkedin_df["categories"].str.contains(linkedin_filter, na=False)] if linkedin_filter != "All" else linkedin_df
    st.metric("Total postings", len(linkedin_display))
    st.dataframe(linkedin_display[["title", "company", "location"]], use_container_width=True)

with tab5:
    counts = {}
    for cat in CATEGORIES:
        total = sum(d["categories"].str.contains(cat, na=False).sum() for d in [blogs_df, jobs_df, linkedin_df])
        counts[cat] = total
    counts_df = pd.DataFrame(list(counts.items()), columns=["Category", "Count"])
    st.bar_chart(counts_df.set_index("Category"))

conn.close()