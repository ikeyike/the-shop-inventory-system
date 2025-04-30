
import re
import requests
import gspread
import csv
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import quote
from difflib import SequenceMatcher

# ---------------- CONFIG ------------------
GOOGLE_SHEET_NAME = "Hot Wheels and Matchbox Inventory"
SHEET_TAB_NAME = "Test"
LOG_FILE = "wiki_scraper_log.csv"
COLUMNS_TO_UPDATE = {
    "Collector #": "col",
    "Series #": "series",
    "Body Color": "color",
    "Base Color/Type": "basecolor",
    "Country": "country",
    "Wheel Type": "wheeltype"
}
# -----------------------------------------

def clean(text):
    return re.sub(r"[^a-z0-9]+", "", str(text).lower().strip())

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def log_to_csv(row_num, model_name, toy_num, status, url):
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([row_num, model_name, toy_num, status, url])

def extract_table_rows(soup):
    tables = soup.find_all("table", class_="wikitable")
    for table in tables:
        raw_headers = [th.get_text(strip=True) for th in table.find_all("th")]
        headers = [clean(h) for h in raw_headers]
        if "toy" in "".join(headers) and "color" in "".join(headers):
            print("✅ Versions table found.")
            rows = []
            for tr in table.find_all("tr")[1:]:
                cells = tr.find_all(["td", "th"])
                row_data = [cell.get_text(strip=True).replace("\xa0", " ") for cell in cells]
                if len(row_data) == len(headers):
                    row_dict = dict(zip(headers, row_data))
                    rows.append(row_dict)
            return rows
    print("⚠️ No valid Versions table found.")
    return []

def build_wiki_url(model_name, brand):
    base_url = "https://hotwheels.fandom.com/wiki/" if brand.lower() == "hot wheels" else "https://matchbox.fandom.com/wiki/"
    model_cleaned = model_name.replace("’", "'").split(" (")[0]
    encoded_name = quote(model_cleaned, safe="_()")
    return base_url + encoded_name

def get_wiki_versions(toy_number, model, brand, year):
    url = build_wiki_url(model, brand)
    print(f"🔍 Fetching: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print("⚠️ Page not found.")
            return None, url
        soup = BeautifulSoup(response.text, "html.parser")
        table_data = extract_table_rows(soup)

        for row in table_data:
            toy_key = next((k for k in row if "toy" in k), None)
            if toy_key:
                wiki_toy = clean(row.get(toy_key, ""))
                input_toy = clean(toy_number)
                print(f"   ↪️ Comparing {input_toy} with {wiki_toy}")
                if input_toy == wiki_toy or input_toy in wiki_toy:
                    return row, url

        # If no exact or partial match, try fuzzy matching
        for row in table_data:
            toy_key = next((k for k in row if "toy" in k), None)
            if toy_key:
                similarity = similar(clean(toy_number), clean(row.get(toy_key, "")))
                if similarity > 0.85:
                    print("🔁 Fuzzy match used.")
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

    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Row", "Model Name", "Toy #", "Status", "Wiki URL"])

    for idx, row in enumerate(records, start=2):
        if not row.get("Toy #") or not row.get("Model Name"): continue
        brand = row.get("Brand", "Hot Wheels")
        year = row.get("Year", "")
        print(f"🔍 Row {idx}: {row['Model Name']} → {row['Toy #']}")
        data, page_url = get_wiki_versions(row["Toy #"], row["Model Name"], brand, year)
        if data:
            updates = {}
            for sheet_col, wiki_key in COLUMNS_TO_UPDATE.items():
                wiki_value = next((data.get(k) for k in data if wiki_key in k), None)
                if wiki_value:
                    updates[sheet_col] = wiki_value
            if updates:
                print(f"✅ Updating Row {idx}: {updates}")
                for col_name, val in updates.items():
                    col_index = header.index(col_name) + 1
                    sheet.update_cell(idx, col_index, val)
                log_to_csv(idx, row["Model Name"], row["Toy #"], "Updated", page_url)
            else:
                log_to_csv(idx, row["Model Name"], row["Toy #"], "No Relevant Data", page_url)
        else:
            log_to_csv(idx, row["Model Name"], row["Toy #"], "No Data", page_url)

if __name__ == "__main__":
    main()
