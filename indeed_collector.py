import random
import time
import os
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_indeed(query="informatique", location="Maroc", base_url="https://ma.indeed.com", pages=3):
    driver = init_driver()
    jobs = []

    for page in range(pages):
        start = page * 10
        url = f"{base_url}/jobs?q={query}&l={location}&start={start}"
        print(f"[+] Fetching page {page + 1}: {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.job_seen_beacon, td.resultContent")
                )
            )
        except Exception:
            print("[!] Page took too long to load or triggered a Cloudflare challenge.")
            break

        time.sleep(random.uniform(2.0, 4.0))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.find_all("div", class_="job_seen_beacon") or soup.find_all("td", class_="resultContent")

        if not cards:
            print("[!] No more postings found, stopping.")
            break

        print(f"[+] Found {len(cards)} postings on this page.")

        for card in cards:
            title_elem = (
                card.find("a", class_="jcs-JobTitle")
                or card.find("h2", class_="jobTitle")
                or card.find("span", {"id": lambda x: x and x.startswith("jobTitle")})
            )
            title = ""
            if title_elem:
                title = (
                    title_elem.get("title")
                    or title_elem.get_text(strip=True)
                    or (title_elem.find("span").get_text(strip=True) if title_elem.find("span") else "")
                )

            company_elem = card.find("span", {"data-testid": "company-name"}) or card.find("span", class_="companyName")
            company = company_elem.get_text(strip=True) if company_elem else ""

            location_elem = card.find("div", {"data-testid": "text-location"}) or card.find("div", class_="companyLocation")
            loc = location_elem.get_text(strip=True) if location_elem else ""

            jobs.append({"source": "indeed", "title": title, "company": company, "location": loc})

        time.sleep(random.uniform(3.0, 5.0))

    driver.quit()
    return jobs


if __name__ == "__main__":
    import time as t
    QUERIES = ["informatique", "développeur", "data", "devops", "cybersécurité"]
    all_jobs = []

    for q in QUERIES:
        print(f"\n=== Recherche: {q} ===")
        jobs = scrape_indeed(query=q, location="Maroc", pages=2)
        all_jobs.extend(jobs)
        t.sleep(random.uniform(5, 8))

    if all_jobs:
        new_df = pd.DataFrame(all_jobs)
        if os.path.exists("indeed_jobs.csv"):
            existing_df = pd.read_csv("indeed_jobs.csv")
            existing_count = len(existing_df)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            existing_count = 0
            combined_df = new_df

        combined_df = combined_df.drop_duplicates(subset="title")
        print(f"\n[+] {existing_count} existing + new postings -> {len(combined_df)} total unique")
        combined_df.to_csv("indeed_jobs.csv", index=False)
    else:
        print("[-] No data extracted.")