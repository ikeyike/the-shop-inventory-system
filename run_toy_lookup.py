
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from toy_metadata import get_product_info
import time

# -------------------- SETUP --------------------

SPREADSHEET_NAME = "Hot Wheels and Matchbox Inventory"
WORKSHEET_NAME = "Test"
CREDENTIALS_FILE = "credentials.json"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

# -------------------- TARGET COLUMNS --------------------

columns_to_fill = [
    "Collector #", "Brand", "Year", "Model Name", "Series", "Series #",
    "Body Color", "Base", "Wheels", "hobbydb Price"
]

headers = sheet.row_values(1)

col_indices = {}
missing_columns = []

for col in columns_to_fill:
    if col in headers:
        col_indices[col] = headers.index(col) + 1
    else:
        missing_columns.append(col)

if missing_columns:
    print("⚠️ Skipping missing columns:", ", ".join(missing_columns))

toy_col_index = headers.index("Toy #") + 1
records = sheet.get_all_records()

# -------------------- MAIN LOOP --------------------

for idx, row in enumerate(records, start=2):  # skip header row
    toy_number = str(row.get("Toy #", "")).strip()
    if not toy_number:
        continue

    needs_update = any(not row.get(col) for col in col_indices.keys())
    if not needs_update:
        continue

    print(f"🔍 Fetching: Toy # {toy_number} (Row {idx})")
    data = get_product_info(toy_number)
    time.sleep(2)  # polite delay

    if not data:
        print(f"⚠️ No data found for Toy #: {toy_number}")
        continue

    for col, value in data.items():
        if col in col_indices and value and not row.get(col):
            sheet.update_cell(idx, col_indices[col], value)
            print(f"  ➤ Updated '{col}'")

    print(f"✅ Row {idx} updated for Toy #: {toy_number}")

print("🎉 Done updating all rows.")
