import random
import time
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


def scrape_indeed(
    query="informatique", location="Maroc", base_url="https://ma.indeed.com"
):
  driver = init_driver()
  jobs = []

  url = f"{base_url}/jobs?q={query}&l={location}"
  print(f"[+] Fetching: {url}")
  driver.get(url)

  try:
    WebDriverWait(driver, 12).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.job_seen_beacon, td.resultContent")
        )
    )
  except Exception:
    print(
        "[!] Page took too long to load or triggered a Cloudflare challenge."
    )

  time.sleep(random.uniform(2.0, 4.0))

  soup = BeautifulSoup(driver.page_source, "html.parser")
  cards = soup.find_all("div", class_="job_seen_beacon")
  if not cards:
    cards = soup.find_all("td", class_="resultContent")

  print(f"[+] Found {len(cards)} postings.")

  for card in cards[:20]:
    # Targeted title extraction
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
          or (
              title_elem.find("span").get_text(strip=True)
              if title_elem.find("span")
              else ""
          )
      )

    company_elem = card.find("span", {"data-testid": "company-name"}) or (
        card.find("span", class_="companyName")
    )
    company = company_elem.get_text(strip=True) if company_elem else ""

    location_elem = card.find("div", {"data-testid": "text-location"}) or (
        card.find("div", class_="companyLocation")
    )
    loc = location_elem.get_text(strip=True) if location_elem else ""

    snippet_elem = (
        card.find("div", class_="underShelfFooter")
        or card.find("ul", class_="css-18z7g9h")
        or card.find("div", class_="job-snippet")
        or card.find("td", class_="snip")
    )
    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

    jobs.append({
        "source": "indeed",
        "title": title,
        "company": company,
        "location": loc,
        "summary": snippet,
    })

  driver.quit()
  return jobs


if __name__ == "__main__":
  job_data = scrape_indeed(query="informatique", location="Maroc")

  if job_data:
    df = pd.DataFrame(job_data)
    print("\n--- Scraped Results ---")
    print(df[["title", "company", "location"]].head(10))
    df.to_csv("indeed_jobs.csv", index=False)
    print("\n[+] Saved to indeed_jobs.csv")
  else:
    print("[-] No data extracted.")