
import csv
from datetime import datetime

LOG_FILE = "wiki_scraper_log.csv"

def log_to_csv(row_index, model_name, toy_number, status, source_url=""):
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), row_index, model_name, toy_number, status, source_url])


import re
import requests
import gspread
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- CONFIG ------------------
GOOGLE_SHEET_NAME = "Hot Wheels and Matchbox Inventory"
SHEET_TAB_NAME = "Test"
COLUMNS_TO_UPDATE = {
    "Collector #": "col #",
    "Series #": "series",
    "Body Color": "color",
    "Base Color/Type": "base color",
    "Country": "country",
    "Wheel Type": "wheel type"
}
BASE_URLS = {
    "Hot Wheels": "https://hotwheels.fandom.com/wiki/",
    "Matchbox": "https://matchbox.fandom.com/wiki/"
}
# -----------------------------------------

def clean(text):
    return re.sub(r"[^a-z0-9]+", "", str(text).lower().strip())

def extract_table_rows(soup):
    for table in soup.find_all("table", class_="wikitable"):
        headers = [clean(th.get_text()) for th in table.find_all("th")]
        if "toy" in "".join(headers) and "color" in "".join(headers):
            print("✅ Versions table found.")
            rows = []
            for tr in table.find_all("tr")[1:]:
                cells = tr.find_all(["td", "th"])
                row_data = [cell.get_text(strip=True).replace("\xa0", " ") for cell in cells]
                if len(row_data) == len(headers):
                    rows.append(dict(zip(headers, row_data)))
            return rows
    print("⚠️ No valid Versions table found.")
    return []

def get_versions_data(toy_number, model, brand):
    url_base = BASE_URLS.get(brand, BASE_URLS["Hot Wheels"])
    model_cleaned = model.replace("’", "'").replace(" ", "_").replace("'", "%27")
    url = url_base + model_cleaned
    print(f"🔍 Fetching: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print("⚠️ Page not found.")
            return None, None
        soup = BeautifulSoup(response.text, "html.parser")
        for row in extract_table_rows(soup):
            if clean(toy_number) in clean(row.get("toy #", "")):
                return row, url
        print(f"⚠️ No match for Toy #: {toy_number}")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    return None, url

def main():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).worksheet(SHEET_TAB_NAME)
    records = sheet.get_all_records()
    header = sheet.row_values(1)

    for idx, row in enumerate(records, start=2):
        if not row.get("Toy #") or not row.get("Model Name") or not row.get("Brand"):
            continue
        print(f"🔍 Row {idx}: {row['Model Name']} → {row['Toy #']}")
        data, page_url = get_versions_data(row["Toy #"], row["Model Name"], row["Brand"])
        if data:
            updates = {col: data[wiki_col] for col, wiki_col in COLUMNS_TO_UPDATE.items() if wiki_col in data}
            if updates:
                print(f"✅ Updating Row {idx}: {updates}")
                log_to_csv(idx, row['Model Name'], row['Toy #'], 'Updated', page_url)
                for col_name, val in updates.items():
                    col_index = header.index(col_name) + 1
                    sheet.update_cell(idx, col_index, val)
        else:
            print(f"⚠️ No data found for Row {idx}")
            log_to_csv(idx, row['Model Name'], row['Toy #'], 'No Data', page_url)

if __name__ == "__main__":
    main()
