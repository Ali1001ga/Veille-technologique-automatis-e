import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Veille Technologique IT/Data", page_icon="📊", layout="wide")

st.markdown("""
<style>
h1 { color: #E2E8F0 !important; font-weight: 700; }
h2, h3 { color: #4FD1C5 !important; font-weight: 600; }

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #4FD1C5 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: #4FD1C5 !important;
}

[data-testid="stMetric"] {
    background-color: #1A2332;
    border: 1px solid #2D3B4E;
    border-radius: 10px;
    padding: 16px;
}
[data-testid="stMetricValue"] {
    color: #4FD1C5 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #2D3B4E;
    border-radius: 8px;
    overflow: hidden;
}

hr, [data-testid="stTabs"] {
    border-color: #2D3B4E !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Veille Technologique — Tendances IT/Data Maroc & France")

st.caption("Collecte, classification et suivi automatisés des tendances IT/Data — Maroc & France")

from datetime import datetime
st.caption(f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")

conn = sqlite3.connect("veille.db")
CATEGORIES = ["Cloud", "Data", "DevOps", "AI", "Cybersecurity"]

blogs_df = pd.read_sql("SELECT * FROM blog_posts", conn)
jobs_df = pd.read_sql("SELECT * FROM indeed_jobs", conn)
linkedin_df = pd.read_sql("SELECT * FROM linkedin_jobs", conn)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Google Trends", "Blog Posts", "Indeed", "LinkedIn", "Indicateurs"])

with tab1:
    country = st.selectbox("Country", ["Morocco", "France"])
    table = "trends_morocco" if country == "Morocco" else "trends_france"
    trends_df = pd.read_sql(f"SELECT * FROM {table}", conn)
    trends_df["date"] = pd.to_datetime(trends_df["date"])

    min_date, max_date = trends_df["date"].min(), trends_df["date"].max()
    date_range = st.date_input("Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = trends_df[(trends_df["date"] >= start) & (trends_df["date"] <= end)]
    else:
        filtered = trends_df

    st.line_chart(filtered.set_index("date"))

    st.subheader("Tendances émergentes vs en déclin (8 dernières semaines vs 8 précédentes)")
    keyword_cols = [c for c in filtered.columns if c != "date"]
    trend_summary = []
    for col in keyword_cols:
        recent = filtered[col].tail(8).mean()
        previous = filtered[col].iloc[-16:-8].mean() if len(filtered) >= 16 else filtered[col].head(8).mean()
        change = ((recent - previous) / previous * 100) if previous > 0 else 0
        trend_summary.append({"Keyword": col, "Change (%)": round(change, 1)})
    st.dataframe(pd.DataFrame(trend_summary).sort_values("Change (%)", ascending=False), width="stretch")  

with tab2:
    blog_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="blog_filter")
    blogs_display = blogs_df[blogs_df["categories"].str.contains(blog_filter, na=False)] if blog_filter != "All" else blogs_df
    st.metric("Total posts", len(blogs_display))
    st.dataframe(blogs_display[["source", "title", "categories"]], width="stretch")

with tab3:
    indeed_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="indeed_filter")
    jobs_display = jobs_df[jobs_df["categories"].str.contains(indeed_filter, na=False)] if indeed_filter != "All" else jobs_df
    st.metric("Total postings", len(jobs_display))
    st.dataframe(jobs_display[["title", "company", "location"]], width="stretch")

with tab4:
    linkedin_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="linkedin_filter")
    linkedin_display = linkedin_df[linkedin_df["categories"].str.contains(linkedin_filter, na=False)] if linkedin_filter != "All" else linkedin_df
    st.metric("Total postings", len(linkedin_display))
    st.dataframe(linkedin_display[["title", "company", "location"]], width="stretch")

with tab5:
    counts = {}
    for cat in CATEGORIES:
        total = sum(d["categories"].str.contains(cat, na=False).sum() for d in [blogs_df, jobs_df, linkedin_df])
        counts[cat] = total
    counts_df = pd.DataFrame(list(counts.items()), columns=["Category", "Count"])
    st.bar_chart(counts_df.set_index("Category"))

conn.close()