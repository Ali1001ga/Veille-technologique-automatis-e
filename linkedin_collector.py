import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_linkedin(keyword="informatique", location="Morocco"):
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location={location}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    cards = soup.find_all("div", class_="base-card")
    print(f"[+] Found {len(cards)} postings.")

    for card in cards[:20]:
        title_elem = card.find("h3", class_="base-search-card__title")
        company_elem = card.find("h4", class_="base-search-card__subtitle")
        location_elem = card.find("span", class_="job-search-card__location")

        jobs.append({
            "source": "linkedin",
            "title": title_elem.get_text(strip=True) if title_elem else "",
            "company": company_elem.get_text(strip=True) if company_elem else "",
            "location": location_elem.get_text(strip=True) if location_elem else ""
        })

    return jobs

if __name__ == "__main__":
    job_data = scrape_linkedin(keyword="informatique", location="Morocco")
    df = pd.DataFrame(job_data)
    print(df.head(20))
    df.to_csv("linkedin_jobs.csv", index=False)
    print(f"[+] Saved {len(df)} postings")