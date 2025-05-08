
import os
import glob
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'
ID_COLUMN = 'A'
VARIANT_COLUMN = 'M'
IMAGE_COLUMNS = ['N', 'O', 'P', 'Q', 'R']

def authenticate_google_services():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return sheets_service, drive_service

def update_sheet_with_links(sheets_service, toy_number, variant, image_links):
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!{ID_COLUMN}:{VARIANT_COLUMN}").execute()
    values = result.get('values', [])

    for idx, row in enumerate(values):
        if row and row[0] == toy_number and row[1] == variant:
            row_index = idx + 1
            data = [{
                'range': f"{SHEET_NAME}!{col}{row_index}",
                'values': [[link]] if i < len(image_links) else [[""]]
            } for i, col in enumerate(IMAGE_COLUMNS)]
            body = {'valueInputOption': 'USER_ENTERED', 'data': data}
            sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
            print(f"Updated row {row_index} for {toy_number} - {variant}")
            return

    print(f"Entry not found for {toy_number} - {variant}.")

if __name__ == "__main__":
    product_id = input("Enter Toy # (e.g., M6916): ").strip()
    variant = input("Enter Variant (e.g., Red, Blue): ").strip()
    folder_path = os.path.join("/Users/naomiabella/Desktop/the_shop_inventory/organized_images", f"{product_id}-{variant}")

    sheets_service, drive_service = authenticate_google_services()
    image_files = sorted(glob.glob(os.path.join(folder_path, '*.*')))
    image_links = [f"https://drive.google.com/uc?id={os.path.basename(f)}" for f in image_files]

    update_sheet_with_links(sheets_service, product_id, variant, image_links)
