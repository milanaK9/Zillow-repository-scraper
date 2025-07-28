import random
import time
from marshal import dumps

import requests
import playwright
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

import pyzill
import json


from playwright.sync_api import sync_playwright
import json


import urllib.parse
import json
from typing import Any, Optional
from curl_cffi import requests
from playwright.sync_api import sync_playwright

sq = input("Enter search query")

def get_zillow_json(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1280, "height": 800}
        )

        # Anti-bot stealth tweaks
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page = context.new_page()
        print(f"🔍 Visiting: {url}")
        page.goto(url)
        # page.wait_for_load_state("networkidle")

        # Allow page scripts to finish
        time.sleep(3)

        try:
            raw_json = page.query_selector('#__NEXT_DATA__').text_content()
            zillow_data = json.loads(raw_json)

            return zillow_data

        except Exception as e:
            print(f"❌ Error extracting searchQueryState: {e}")
            return None

        finally:
            browser.close()
def get_info(search_query):
    zillow_data = get_zillow_json(f"https://www.zillow.com/{search_query.strip().replace(' ', '-').lower()}")
    #search_query_state = zillow_data["props"]["pageProps"]["searchPageState"]['queryState']
    total_pages = zillow_data["props"]["pageProps"]["searchPageState"]['cat1']['searchList']['totalPages']
    print("✅ totalPages extracted!")
    return  total_pages


props = []
total_pages = get_info(sq)

for i in range(total_pages):
    time.sleep(random.uniform(2, 5))
    url = "https://www.zillow.com/" + sq.strip().replace(' ', '-').lower() + "/" \
           + str(i + 1) + "_p" + "/"

    zillow_data = get_zillow_json(url)
    for prop in zillow_data["props"]["pageProps"]["searchPageState"]['cat1']['searchResults']['listResults']:
        props.append({
            "Price": prop.get("price"),
            "Address": prop.get("address"),
            "Bedrooms": prop.get("beds", "N/A"),
            "Bathrooms": prop.get("baths", "N/A"),
            "Living Area (sqft)": str(prop.get("area")) + " sqft" if prop.get("area", None) else "N/A",
            "Property Link": prop.get("detailUrl", ""),
            "Latitude": prop.get("latLong", {}).get("latitude"),
            "Longitude": prop.get("latLong", {}).get("longitude"),
        })



import pandas as pd

df = pd.DataFrame(props)
df.to_excel("properties.xlsx", index=False)

import csv

keys = props[0].keys()  # column headers

with open("properties.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    writer.writerows(props)
