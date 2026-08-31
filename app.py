import streamlit as st
import pandas as pd
import sqlite3

st.title("Veille Technologique - IT/Data Trends Dashboard")

conn = sqlite3.connect("veille.db")

st.header("Google Trends")
country = st.selectbox("Country", ["Morocco", "France"])
table = "trends_morocco" if country == "Morocco" else "trends_france"
trends_df = pd.read_sql(f"SELECT * FROM {table}", conn)
st.line_chart(trends_df.set_index("date")[["Python", "Docker", "AWS"]])

st.header("Blog Posts")
blogs_df = pd.read_sql("SELECT * FROM blog_posts", conn)
category_filter = st.selectbox("Filter by category", ["All", "Cloud", "Data", "DevOps", "AI"])
if category_filter != "All":
    blogs_df = blogs_df[blogs_df["categories"].str.contains(category_filter, na=False)]
st.dataframe(blogs_df[["source", "title", "categories"]])

st.header("Indeed Job Postings")
jobs_df = pd.read_sql("SELECT * FROM indeed_jobs", conn)
st.dataframe(jobs_df[["title", "company", "location", "categories"]])

st.header("LinkedIn Job Postings")
linkedin_df = pd.read_sql("SELECT * FROM linkedin_jobs", conn)
st.dataframe(linkedin_df[["title", "company", "location", "categories"]])

conn.close()