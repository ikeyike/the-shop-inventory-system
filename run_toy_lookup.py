
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from toy_metadata import get_product_info

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
col_indices = {col: headers.index(col) + 1 for col in columns_to_fill}
toy_col_index = headers.index("Toy #") + 1

# -------------------- MAIN --------------------

toy_number = input("Enter Toy #: ").strip()
if not toy_number:
    print("❌ No Toy # entered. Exiting.")
    exit()

scraped_info = get_product_info(toy_number)
if not scraped_info:
    print("⚠️ No data found.")
    exit()

print("\n✅ Data found:")
for k, v in scraped_info.items():
    print(f"{k}: {v}")

# Find matching row in Google Sheet
records = sheet.get_all_records()
row_to_update = None

for idx, row in enumerate(records, start=2):  # start=2 for 1-based indexing and skipping header
    if str(row.get("Toy #")).strip().lower() == toy_number.lower():
        row_to_update = idx
        break

if not row_to_update:
    print("⚠️ No matching row with this Toy # found in your Google Sheet.")
    exit()

confirm = input("\nDo you want to update this row with the data? (y/n): ").strip().lower()
if confirm != "y":
    print("❌ Canceled. No changes made.")
    exit()

# Update Google Sheet
for col, value in scraped_info.items():
    if col in columns_to_fill and value:
        existing_value = sheet.cell(row_to_update, col_indices[col]).value
        if not existing_value:
            sheet.update_cell(row_to_update, col_indices[col], value)

print(f"✅ Updated row {row_to_update} with product info for Toy #: {toy_number}")
