import json
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver

BASE_URL = "https://www.thegradcafe.com"


def _get_driver():
    driver = webdriver.Chrome()
    return driver


def _get_next_page_url(soup):
    nav = soup.find("nav", attrs={"aria-label": "Results pagination"})
    if not nav:
        return None
    for a_tag in nav.find_all("a"):
        if "Next" in a_tag.get_text():
            return a_tag.get("href")
    return None


def _parse_badges(badge_texts):
    result = {"term": None, "origin": None, "GPA": None, "GRE": None, "GRE V": None, "GRE AW": None}
    for text in badge_texts:
        if re.match(r"^(Fall|Spring)\s+\d{4}$", text):
            result["term"] = text
        elif text in ("American", "International", "Other"):
            result["origin"] = text
        elif text.startswith("GRE AW "):
            result["GRE AW"] = text.replace("GRE AW ", "")
        elif text.startswith("GRE V "):
            result["GRE V"] = text.replace("GRE V ", "")
        elif text.startswith("GRE "):
            result["GRE"] = text.replace("GRE ", "")
        elif text.startswith("GPA "):
            result["GPA"] = text.replace("GPA ", "")
    return result


def _parse_entry(anchor_row):
    a_tag = anchor_row.find("a", href=re.compile(r"^/result/\d+"))
    if not a_tag:
        return None

    cells = anchor_row.find_all("td")
    if len(cells) < 4:
        return None

    school_div = cells[0].find("div", class_="tw-font-medium")
    school = school_div.get_text(strip=True) if school_div else None

    spans = cells[1].find_all("span")
    program = spans[0].get_text(strip=True) if len(spans) > 0 else None
    degree = spans[1].get_text(strip=True) if len(spans) > 1 else None

    added_on = cells[2].get_text(strip=True)
    decision = cells[3].get_text(strip=True)

    entry = {
        "university": school,
        "program": program,
        "degree": degree,
        "added_on": added_on,
        "status": decision,
        "url": "https://www.thegradcafe.com" + a_tag["href"],
        "comments": None,
    }

    badge_row = anchor_row.find_next_sibling("tr")
    if badge_row:
        badge_container = badge_row.find("div", class_="tw-gap-2")
        if badge_container:
            badge_texts = [d.get_text(strip=True) for d in badge_container.find_all("div", recursive=False)]
            entry.update(_parse_badges(badge_texts))

        comment_row = badge_row.find_next_sibling("tr")
        if comment_row:
            p_tag = comment_row.find("p", class_="tw-text-gray-500 tw-text-sm tw-my-0")
            if p_tag:
                entry["comments"] = p_tag.get_text(strip=True)

    return entry


def scrape_data(max_pages=150):
    driver = _get_driver()
    all_records = []

    try:
        url = BASE_URL + "/survey/"
        page_count = 0

        while url and page_count < max_pages:
            page_count += 1
            print(f"Scraping page {page_count}: {url}")

            driver.get(url)
            time.sleep(1)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            rows = soup.find_all("tr")
            anchor_rows = [r for r in rows if r.find("a", href=re.compile(r"^/result/\d+"))]

            print(f"Entries found: {len(anchor_rows)}")

            for row in anchor_rows:
                entry = _parse_entry(row)
                if entry:
                    all_records.append(entry)

            if len(all_records) % 200 < len(anchor_rows):
                print(f"Checkpoint saved at {len(all_records)} records")
                save_data(all_records)

            url = _get_next_page_url(soup)
            time.sleep(0.5)

    finally:
        driver.quit()

    return all_records


def save_data(data, filename="applicant_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    data = scrape_data(max_pages=1000)
    save_data(data)

    print(f"Saved {len(data)} raw records")