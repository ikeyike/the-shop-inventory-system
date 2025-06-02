import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# === Config ===
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'

# Zero-based column indexes (A=0, ..., J=9, L=11, N=13)
TOY_COLUMN_INDEX = 0
VARIANT_COLUMN_INDEX = 9
BOX_COLUMN_INDEX = 11
CHECKMARK_COLUMN_INDEX = 15

CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# === Paths ===
GOOGLE_DRIVE_UPLOAD_DIR = "/Users/ikeyike/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
CHECKLIST_FILE = "/Users/ikeyike/Desktop/the_shop_inventory/variant_checklist.csv"

def main():
    os.makedirs(GOOGLE_DRIVE_UPLOAD_DIR, exist_ok=True)

    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    range_str = f"{SHEET_NAME}!A:S"
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range_str).execute()
    values = result.get('values', [])

    lines = []

    for row in values[1:]:  # Skip header row
        if len(row) <= max(TOY_COLUMN_INDEX, VARIANT_COLUMN_INDEX, BOX_COLUMN_INDEX):
            continue

        toy_num = row[TOY_COLUMN_INDEX].strip()
        variant = row[VARIANT_COLUMN_INDEX].strip()
        box_raw = row[BOX_COLUMN_INDEX].strip()
        checkmark = row[CHECKMARK_COLUMN_INDEX].strip() if len(row) > CHECKMARK_COLUMN_INDEX else ""

        if not toy_num or not variant:
            continue  # Skip if Toy # or Variant is empty
        if checkmark:
            continue  # Skip if already marked as uploaded

        print(f"👀 Processing: Toy #{toy_num} | Box: '{box_raw}' | Variant: '{variant}'")

        try:
            if int(float(box_raw)) == 3:
                folder_name = f"{toy_num}-{variant}"
                folder_path = os.path.join(GOOGLE_DRIVE_UPLOAD_DIR, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                print(f"📁 Created: {folder_path}")
                lines.append(f"{toy_num} → ✅ Variant: {variant} ✅ Box 3")
        except ValueError:
            print(f"⚠️ Could not interpret Box # for {toy_num}: '{box_raw}'")

    with open(CHECKLIST_FILE, "w") as f:
        f.write("\n".join(lines))

    print(f"\n✅ Folders created for Box 3 with variant values in:\n{GOOGLE_DRIVE_UPLOAD_DIR}")
    print(f"📋 Checklist saved to:\n{CHECKLIST_FILE}")

if __name__ == "__main__":
    main()