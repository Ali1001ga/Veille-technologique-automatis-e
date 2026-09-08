import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_linkedin(keyword, location, pages=2):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

    for page in range(pages):
        start = page * 25
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location={location}&start={start}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        if not cards:
            break

        for card in cards:
            title_elem = card.find("h3", class_="base-search-card__title")
            company_elem = card.find("h4", class_="base-search-card__subtitle")
            location_elem = card.find("span", class_="job-search-card__location")
            jobs.append({
                "source": "linkedin",
                "title": title_elem.get_text(strip=True) if title_elem else "",
                "company": company_elem.get_text(strip=True) if company_elem else "",
                "location": location_elem.get_text(strip=True) if location_elem else ""
            })
        time.sleep(2)
    return jobs

if __name__ == "__main__":
    QUERIES = ["informatique", "développeur", "data", "devops", "cybersécurité"]
    LOCATIONS = ["Morocco", "France"]
    all_jobs = []

    for loc in LOCATIONS:
        for q in QUERIES:
            print(f"=== {q} — {loc} ===")
            jobs = scrape_linkedin(q, loc)
            print(f"[+] {len(jobs)} found")
            all_jobs.extend(jobs)
            time.sleep(2)

    new_df = pd.DataFrame(all_jobs)
    if os.path.exists("linkedin_jobs.csv"):
        existing_df = pd.read_csv("linkedin_jobs.csv")
        existing_count = len(existing_df)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        existing_count = 0
        combined_df = new_df

    combined_df = combined_df.drop_duplicates(subset="title")
    print(f"[+] {existing_count} existing + new -> {len(combined_df)} total unique")
    combined_df.to_csv("linkedin_jobs.csv", index=False)