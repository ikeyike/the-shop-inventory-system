import os
import glob
import csv
import shutil
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# === Config ===
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'
ID_COLUMN = 'A'
VARIANT_COLUMN = 'J'
IMAGE_COLUMNS = ['N', 'O']
CHECKMARK_COLUMN = 'P'
LOG_FILE = "/Users/ikeyike/Desktop/the_shop_inventory/processed_images.csv"

# Folder structure
BASE_FOLDER = "/Users/ikeyike/Desktop/the_shop_inventory/organized_images"
ARCHIVE_DIR = "/Users/ikeyike/Desktop/the_shop_inventory/archive"

ARCHIVE_PROCESSED = False  # Toggle archiving

def authenticate_google_services():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return sheets_service, drive_service

def upload_to_drive(drive_service, file_path):
    folder_id = os.getenv("DRIVE_UPLOAD_FOLDER_ID")
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    # Create new MediaFileUpload instance per call
    media = MediaFileUpload(file_path, resumable=False)

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Make file public
    drive_service.permissions().create(
        fileId=file['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    public_url = f"https://drive.google.com/uc?id={file['id']}"
    return public_url

def log_processed_image(file_path, toy_number, variant, status):
    with open(LOG_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([file_path, toy_number, variant, status])

def mark_as_uploaded(sheet_service, row_index):
    update_range = f"{SHEET_NAME}!{CHECKMARK_COLUMN}{row_index}"
    body = {"values": [["✔"]]}
    sheet_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=update_range,
        valueInputOption="RAW",
        body=body
    ).execute()

def update_sheet_with_links(sheets_service, toy_number, variant, image_links):
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!{ID_COLUMN}:{CHECKMARK_COLUMN}"
    ).execute()
    values = result.get('values', [])

    for idx, row in enumerate(values):
        sheet_toy = row[0].strip() if len(row) > 0 else ""
        sheet_variant = row[9].strip() if len(row) > 9 else ""  # Column J = index 9

        if sheet_toy == toy_number and sheet_variant.lower() == variant.lower():
            row_index = idx + 1
            data = [{
                'range': f"{SHEET_NAME}!{col}{row_index}",
                'values': [[link]] if i < len(image_links) else [[""]]
            } for i, col in enumerate(IMAGE_COLUMNS)]
            body = {'valueInputOption': 'USER_ENTERED', 'data': data}
            sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
            mark_as_uploaded(sheets_service, row_index)
            print(f"✅ Updated row {row_index} for {toy_number} - {variant}")
            return True

    print(f"⚠️ Entry not found for {toy_number} - {variant}.")
    return False

def process_images(folder_path, sheets_service, drive_service, folder_name):
    toy_number = folder_name.split('-')[0]
    variant = folder_name.split('-')[1] if '-' in folder_name else "NA"
    image_files = sorted(glob.glob(os.path.join(folder_path, '*.*')))

    if not image_files:
        print(f"⚠️ No images found in {folder_path}")
        return

    image_links = [upload_to_drive(drive_service, img) for img in image_files]

    update_success = update_sheet_with_links(sheets_service, toy_number, variant, image_links)

    for img_path in image_files:
        status = "Processed" if update_success else "Error"
        log_processed_image(img_path, toy_number, variant, status)

    if update_success:
        if ARCHIVE_PROCESSED:
            os.makedirs(ARCHIVE_DIR, exist_ok=True)
            archive_target = os.path.join(ARCHIVE_DIR, folder_name)
            shutil.move(folder_path, archive_target)
            print(f"📦 Archived {folder_name}")
        else:
            print(f"✅ Skipped archiving (ARCHIVE_PROCESSED=False): {folder_name}")
    else:
        print(f"⚠️ Retaining folder due to upload error: {folder_name}")

def main():
    sheets_service, drive_service = authenticate_google_services()

    for box_folder in os.listdir(BASE_FOLDER):
        box_path = os.path.join(BASE_FOLDER, box_folder)
        if not os.path.isdir(box_path):
            continue

        print(f"📦 Scanning box: {box_folder}")
        for folder_name in os.listdir(box_path):
            folder_path = os.path.join(box_path, folder_name)
            if os.path.isdir(folder_path):
                print(f"➡️ Processing folder: {folder_name}")
                process_images(folder_path, sheets_service, drive_service, folder_name)

if __name__ == "__main__":
    main()



# ♻️ Reduce image columns to 2 and add ✔ upload checkmark to Google Sheet

# Add support for archiving entire Box folders after processing

# - Script now loops through Box folders (e.g., Box 1, Box 2)
# - After processing all product folders inside a Box, the entire Box folder is moved to the archive directory
# ✨ Add ARCHIVE_PROCESSED toggle to control folder archiving after upload

# - Introduced ARCHIVE_PROCESSED = True flag for flexible control during testing
# - Allows skipping archiving while debugging
# - Default behavior still archives successfully uploaded folders

# ✨ Upload images to Google Drive, retrieve file IDs, and update Google Sheets with public links
# - Replaced placeholder `uc?id=` URLs with actual Drive file IDs
# - Made uploaded files publicly accessible
# - Ensured entries without matching Toy # and Variant are retained
# - Optional archiving logic remains configurable
# - Prepped structure for future web hosting or DB migration
