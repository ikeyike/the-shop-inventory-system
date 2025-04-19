import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import re
import urllib.parse

# -------------------- CONFIG --------------------

SPREADSHEET_NAME = "Hot Wheels and Matchbox Inventory"
WORKSHEET_NAME = "Test"
CREDENTIALS_FILE = "credentials.json"
LOG_FILE = "wiki_update_log.csv"

columns_to_fill = [
    "Collector #", "Series", "Series #", "Body Color", "Base Color/Type",
    "Country", "Wheel Type"
]

# -------------------- GOOGLE SHEETS SETUP --------------------

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

headers = sheet.row_values(1)
col_indices = {col: headers.index(col) + 1 for col in columns_to_fill}
records = sheet.get_all_records()

# -------------------- UTILS --------------------

def clean_text(text):
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()

def series_fuzzy_match(expected, found):
    expected_words = clean_text(expected).split()
    found_text = clean_text(found)
    return all(word in found_text for word in expected_words)

def google_fallback_search(model_name, brand):
    base = "hotwheels" if brand.lower() == "hot wheels" else "matchbox"
    query = f"site:{base}.fandom.com {model_name}"
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    print("🔎 Using Google fallback search:", url)
    headers = { "User-Agent": "Mozilla/5.0" }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    first_result = soup.select_one("a[href*='fandom.com/wiki/']")
    if first_result:
        raw_url = first_result["href"]
        clean_url = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query).get("q", [None])[0]
        return clean_url
    return None

def fetch_wiki_data(model_name, brand, year, expected_series):
    base_url = "https://hotwheels.fandom.com/wiki/"
    if brand.lower() == "matchbox":
        base_url = "https://matchbox.fandom.com/wiki/"

    query = model_name.replace(" ", "_")
    url = base_url + query
    headers = { "User-Agent": "Mozilla/5.0" }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        url = google_fallback_search(model_name, brand)
        if not url:
            return {}, "NO MATCH"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {}, "FAILED SEARCH"

    soup = BeautifulSoup(response.text, "html.parser")
    info = {}
    series_match = expected_series == ""

    for row in soup.select("aside div.pi-item"):
        label_elem = row.select_one("h3.pi-data-label")
        value_elem = row.select_one("div.pi-data-value")
        if not label_elem or not value_elem:
            continue

        label = label_elem.text.strip().lower()
        value = value_elem.text.strip()

        if "collector" in label:
            info["Collector #"] = value
        elif "series number" in label or "series #" in label:
            info["Series #"] = value
        elif "series" in label and "Series" not in info:
            info["Series"] = value
            if expected_series and series_fuzzy_match(expected_series, value):
                series_match = True
        elif "color" in label and "base" not in label:
            info["Body Color"] = value
        elif "base" in label:
            info["Base Color/Type"] = value
        elif "country" in label or "origin" in label or "made in" in label:
            info["Country"] = value
        elif "wheel" in label:
            info["Wheel Type"] = value

    if expected_series and not series_match:
        print(f"⚠️ Skipping due to fuzzy series mismatch (expected '{expected_series}', got '{info.get('Series', '')}')")
        return {}, url

    return info, url

# -------------------- CSV Logger --------------------

def log_update(row_idx, brand, model_name, year, wiki_url, fields_updated):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            row_idx,
            brand,
            model_name,
            year,
            wiki_url,
            ", ".join(fields_updated)
        ])

# -------------------- MAIN PROCESS --------------------

with open(LOG_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Row", "Brand", "Model Name", "Year", "Wiki URL", "Fields Updated"])

for idx, row in enumerate(records, start=2):
    brand = str(row.get("Brand", "")).strip()
    model = str(row.get("Model Name", "")).strip()
    year = str(row.get("Year", "")).strip()
    series = str(row.get("Series", "")).strip()

    if not brand or not model:
        continue

    needs_update = any(not row.get(col) for col in columns_to_fill)
    if not needs_update:
        continue

    print(f"🔍 Scraping for: {brand} – '{model}' ({year}, Series: {series}) [Row {idx}]")
    data, source_url = fetch_wiki_data(model, brand, year, series)
    time.sleep(2)

    if not data:
        print(f"⚠️ No data found for Row {idx}")
        continue

    updated = []
    for col, value in data.items():
        if col in col_indices and value and not row.get(col):
            sheet.update_cell(idx, col_indices[col], value)
            updated.append(col)

    log_update(idx, brand, model, year, source_url, updated)
    print(f"✅ Updated Row {idx} from {source_url} — Fields: {', '.join(updated)}")

print("🎉 Done with fuzzy-matched series scraping and logging.")