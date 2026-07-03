import json
import time
from urllib.parse import urlencode, urljoin
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

BASE_URL = "https://www.thegradcafe.com"


def main():
    return scrape_data()


def build_url(page):
    params = {"page": page}
    return BASE_URL + "/survey/?" + urlencode(params)


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    return webdriver.Chrome(options=options)


def parse_entry(row):
    cells = row.find_all("td")
    if len(cells) < 4:
        return None

    a_tag = row.find("a", href=True)
    detail_url = urljoin(BASE_URL, a_tag["href"]) if a_tag else None

    return {
        "university": cells[0].get_text(" ", strip=True),
        "program": cells[1].get_text(" ", strip=True),
        "date": cells[2].get_text(" ", strip=True),
        "status": cells[3].get_text(" ", strip=True),
        "url": detail_url,
        "listing": row.get_text(" ", strip=True),
    }


def parse_detail(url):
    try:
        response = session.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        comments_tag = soup.find("p")

        return {
            "comments": comments_tag.get_text(strip=True) if comments_tag else None,
            "raw_text": soup.get_text(" ", strip=True),
        }
    except Exception:
        return {
            "comments": None,
            "raw_text": None,
        }


def scrape_data(pages_to_run=None):
    driver = get_driver()
    all_records = []

    if pages_to_run is None:
        pages_to_run = range(1, 50)  # reduced for stability (1500 is overkill)

    try:
        for page in pages_to_run:
            url = build_url(page)
            print(f"Scraping: {url}")

            driver.get(url)
            time.sleep(0.1)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            rows = soup.find_all("tr")

            print(f"Rows found: {len(rows)}")

            for row in rows:
                entry = parse_entry(row)

                if not entry or not entry["url"]:
                    continue

                try:
                    detail = parse_detail(entry["url"])
                    entry.update(detail)
                    all_records.append(entry)

                    if len(all_records) % 200 == 0:
                        print(f"Checkpoint saved at {len(all_records)} records")
                        save_data(all_records)

                except Exception as e:
                    print("Error scraping", e)

            time.sleep(0.1)

    finally:
        driver.quit()

    return all_records


def save_data(data1, filename="applicant_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data1, f, indent=2)


def fetch_new_records(since=None):
    """
    Worker-compatible wrapper.
    For now we ignore `since` and just run scraper.
    """
    return scrape_data()


if __name__ == "__main__":
    data = scrape_data()
    save_data(data)