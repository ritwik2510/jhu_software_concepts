"""code for scrape.py"""
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
    """main function"""
    return scrape_data()


def build_url(page):
    """builds the URL for a given page"""
    params = {"page": page}
    return BASE_URL + "/survey/?" + urlencode(params)


def get_driver():
    """gets the web driver"""
    driver = webdriver.Chrome
    return driver


def parse_entry(row):
    """parses a single entry from the table row"""
    cells = row.find_all("td")
    if len(cells) < 4:
        return None

    a_tag = row.find("a", href=True)
    detail_url = urljoin("https://www.thegradcafe.com", a_tag["href"]) if a_tag else None

    return {
        "university": cells[0].get_text(" ", strip=True),
        "program": cells[1].get_text(" ", strip=True),
        "date": cells[2].get_text(" ", strip=True),
        "status": cells[3].get_text(" ", strip=True),
        "url": detail_url,
        "listing": row.get_text(" ", strip=True),
    }


def parse_detail(url):
    """parses detail"""
    try:
        response = session.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        comments_tag = soup.find("p")

        return {
            "comments": comments_tag.get_text(strip=True) if comments_tag else None,
            "raw_text": soup.get_text(" ", strip=True),
        }
    except Exception:  # pylint: disable=broad-exception-caught
        return {
            "comments": None,
            "raw_text": None,
        }


def scrape_data(pages_to_run=None):
    """scrapes data"""
    driver = get_driver()
    all_records = []

    if pages_to_run is None:
        pages_to_run = range(1, 1500)

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

                except Exception as e:  # pylint: disable=broad-exception-caught
                    print("Error scraping", e)

            time.sleep(0.1)
    finally:
        driver.quit()

    return all_records


def save_data(data1, filename="applicant_data.json"):
    """saves data"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data1, f, indent=2)


if __name__ == "__main__":
    data = scrape_data()
    save_data(data)
