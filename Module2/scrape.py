import json
import time
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from selenium import webdriver


def build_url(page):

    params = {"page": page}

    return "https://www.thegradcafe.com/survey?" + urlencode(params)

def get_driver():

    driver = webdriver.Chrome()
    return driver


def scrape_data():

    driver = get_driver()

    all_records = []

    for page in range(1, 1000):

        url = build_url(page)

        driver.get(url)

        time.sleep(2)

        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")
