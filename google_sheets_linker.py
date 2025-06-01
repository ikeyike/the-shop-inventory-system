import os
import glob
import csv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'
ID_COLUMN = 'A'
VARIANT_COLUMN = 'M'
IMAGE_COLUMNS = ['N', 'O', 'P', 'Q', 'R']
PROCESSED_LOG = "processed_images.csv"

def authenticate_google_services():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return sheets_service, drive_service

def log_processed_image(file_path, toy_number, variant, status):
    with open(PROCESSED_LOG, "a") as f:
        writer = csv.writer(f)
        writer.writerow([file_path, toy_number, variant, status])

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
            print(f"✅ Updated row {row_index} for {toy_number} - {variant}")
            return True

    print(f"⚠️ Entry not found for {toy_number} - {variant}.")
    return False

def process_images(folder_path, sheets_service):
    toy_number = os.path.basename(folder_path).split('-')[0]
    variant = os.path.basename(folder_path).split('-')[1] if '-' in os.path.basename(folder_path) else "NA"

    image_files = sorted(glob.glob(os.path.join(folder_path, '*.*')))
    if not image_files:
        print(f"⚠️ No images found in {folder_path}")
        return

    image_links = [f"https://drive.google.com/uc?id={os.path.basename(f)}" for f in image_files]

    # Attempt to update Google Sheets
    update_success = update_sheet_with_links(sheets_service, toy_number, variant, image_links)

    # Log and handle deletion based on success
    for img_path in image_files:
        status = "Processed" if update_success else "Error"
        log_processed_image(img_path, toy_number, variant, status)

        if update_success:
            print(f"🗑️ Deleting {img_path} after successful processing...")
            os.remove(img_path)
        else:
            print(f"⚠️ Retaining {img_path} due to error in Google Sheets update.")

if __name__ == "__main__":
    sheets_service, _ = authenticate_google_services()
    
    base_folder = "/Users/ikeyike/Desktop/the_shop_inventory/organized_images"
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            print(f"📦 Processing folder: {folder_name}")
            process_images(folder_path, sheets_service)
