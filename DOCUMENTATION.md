# Veille Technologique — Project Documentation

This file explains, in plain language, what has been built and why. The goal is to be able to explain every piece out loud without notes — this is the working draft for that.

## What the project is

Intelcia currently tracks which tech skills and technologies are in demand in Morocco and France manually — someone checks periodically. This project automates that: it collects data from job postings, tech blogs, and Google search trends, cleans and tags that data to spot which technologies/skills are trending, and shows the results on an interactive dashboard.

The pipeline has four stages: **collect data → clean and tag it → store it → display it on a dashboard.**

## Setup decisions

**Python virtual environment (venv).** Every Python project needs specific library versions. A venv is an isolated folder just for this project's libraries, so they don't clash with anything else on the machine or with other projects. Created with `python -m venv venv`, activated before every work session with `venv\Scripts\activate`.

**Git + GitHub.** The project brief specifically requires a versioned Git repository with a README — this is a standard requirement for showing how the code evolved over time, not just the final result. Every meaningful change is committed with a message describing what changed, and pushed to GitHub as a backup and as the record of progress.

**`.gitignore` excluding `venv/`.** The venv folder contains thousands of installed library files — it shouldn't be tracked in Git, since it's specific to one machine and can always be recreated from a short list of library names. A `.gitignore` file tells Git to skip it entirely.

## Data collection — Google Trends (`trends_collector.py`)

**What it does:** Connects to Google Trends using a library called `pytrends`, and requests search-interest data for a chosen list of tech keywords (currently Python, Docker, AWS), separately for Morocco (`geo='MA'`) and France (`geo='FR'`). Saves the results as two CSV files, `trends_morocco.csv` and `trends_france.csv`.

**Why this source first:** Of the three source types in the brief (job postings, blogs, Google Trends), Trends was built first because it returns clean, structured, ready-to-use numbers with no HTML parsing or scraping involved — the lowest-risk way to prove the whole "collect → save" pattern works before tackling messier sources.

**What the numbers mean:** Google Trends doesn't give raw search counts — it gives a relative popularity score from 0 to 100, where 100 is that keyword's peak popularity within the time window shown. This matters for the soutenance: a score of "39" means "39% as popular as its own peak," not 39 searches.

## Data collection — RSS blogs (`rss_collector.py`)

**What it does:** Pulls recent posts from two tech blogs — Dev.to and Medium — using a library called `feedparser`. For each post it records the source, title, link, and publish date, and saves everything to `blog_posts.csv`.

**Why RSS instead of scraping:** Real web scraping (downloading a page's HTML and picking content out of it) is fragile — sites change their layout, and some actively block bots. Most blogs and news sites publish an RSS feed specifically so other software can read their content in a stable, predictable format without scraping. Using RSS where it's available is a deliberate simplification, not a shortcut that skips the point of the assignment — it collects the same content, more reliably.

**Design choice — a dict of feeds.** The feed URLs are stored in a dictionary (`FEEDS = {"devto": "...", "medium": "..."}`) rather than as separate variables, specifically so a third or fourth source can be added later with one new line, instead of restructuring the code.

## Data collection — Indeed (`indeed_collector.py`)

**What it does:** Uses Selenium (which drives an actual Chrome browser under program control) to load Indeed's public job search results for Morocco (`ma.indeed.com`) and extract the title, company, and location for the first 20 postings. Saves to `indeed_jobs.csv`.

**Why Selenium here but not for blogs:** Indeed's pages are protected by Cloudflare and load content dynamically — a plain `requests` call, which works fine for RSS feeds, doesn't get a usable page back here. Selenium controls a real browser, so it renders the page the same way a human visitor would.

**Login decision:** Confirmed with the supervisor that public, non-authenticated search results are sufficient — so this script never logs in, which avoids any account-related risk entirely.

**Known limitation:** The script's snippet/description extraction doesn't currently match Indeed's live page structure, so the `summary` field comes back empty for every row. Title, company, and location all extract correctly. Given the time available, tagging was scoped to titles only rather than fixing the snippet selectors — a legitimate, documented scope decision rather than an oversight.

## Cleaning and tagging (`tagging.py`)

**What it does:** Applies a category-matching function to both the blog posts and Indeed postings. A dictionary (`CATEGORIES`) maps category names (Cloud, Data, DevOps, AI) to lists of keywords; each post's text is checked for whole-word matches against those lists.

**Why keyword matching instead of a trained NLP model:** Training a real classification model needs labeled data and time neither of which fit a 2-3 week internship. Keyword matching against a curated list is a standard, defensible simplification of the "classification" step the brief asks for, and spaCy's models are still available if more sophisticated processing is added later.

**A real bug that was caught and fixed:** An early version matched keywords as substrings anywhere in the text, which caused false positives — for example, "ai" matched inside unrelated words like "contains" or "explain". This was fixed by switching to whole-word matching (using a regex word-boundary check), and a second bad keyword (a bare "model" matching unrelated data-modeling content) was caught the same way. Both were found by manually inspecting a sample row's raw text against its assigned category, not just trusting the output looked plausible.

## Storage (`store.py`)

**What it does:** Loads all four CSV outputs (Trends x2, tagged blog posts, tagged Indeed jobs) into one SQLite database file, `veille.db`, with each source as its own table.

**Why separate tables instead of one merged table:** The sources don't share the same columns (blog posts have a link and publish date, job postings have a company and location) — forcing them into one shared table would mean a lot of empty/irrelevant fields per row. Keeping each source as its own table inside one database file satisfies the brief's storage requirement while keeping each table's shape meaningful.

## Dashboard (`app.py`)

**What it does:** A Streamlit app reading directly from `veille.db`. Shows a Google Trends line chart with a country selector (Morocco/France), a filterable table of tagged blog posts, and a table of Indeed postings.

## Data collection — LinkedIn (`linkedin_collector.py`)

**What it does:** Fetches job postings from LinkedIn's public "guest" endpoint — a plain HTTP request (via the `requests` library, no browser automation needed) that LinkedIn itself uses to load additional postings. Extracts title, company, and location for up to 20 results per search.

**Why this is lower-risk than it first appeared:** Confirmed with the supervisor that public, non-authenticated description data is sufficient, so this never logs in — no personal account is involved, and no Selenium/browser automation is needed either, since this endpoint returns plain HTML directly. Simpler and lighter-weight than the Indeed script as a result.

## Dashboard redesign (tabs, styling, metrics)

**What changed:** `app.py` restructured from one long stacked page into tabs (Google Trends, Blog Posts, Indeed, LinkedIn, Indicateurs), with `st.set_page_config()` setting a proper browser tab title/icon, `st.metric()` showing post/posting counts per tab, and `use_container_width=True` so tables fill the wider layout.

**Data volume increase:** RSS expanded from 2 feeds to 9 (adding tag-specific Dev.to/Medium feeds), growing from ~21 to 86 posts. LinkedIn added pagination (3 pages), growing from 10 to 29 postings. Indeed's collector now accumulates across multiple runs (loads existing CSV, appends new results, deduplicates by title) instead of overwriting each time, since a single run gets blocked by Cloudflare after page 1 fairly reliably.

**Known constraints:** Google Trends (via pytrends) and Indeed (via Selenium) both hit rate-limiting/anti-bot blocks when run repeatedly in a short window — this is expected behavior for unauthenticated scraping against these services, not a bug, and is why Indeed's script was changed to accumulate over time rather than require one large successful run.

## Remaining work

- **Indeed snippet fix (optional):** revisit the snippet-extraction selectors if time allows, to enable richer tagging beyond title-only for that source.
- **Dashboard polish:** additional filters, styling, and a written weekly-report generator are optional/stretch items from the brief.

---
*Keep this file updated as each new piece is built — add a short "what it does / why this choice" entry before moving to the next piece, not after everything is finished.*
