import os
import glob
import csv
import shutil
import time
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === Load .env file ===
load_dotenv()

# === Script Behavior Toggle ===
ARCHIVE_ENABLED = False  # Set to True to move processed folders to /archive

# === Config ===
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'
ID_COLUMN = 'A'
VARIANT_COLUMN_INDEX = 9  # J is column 10, 0-indexed
IMAGE_COLUMNS = ['N', 'O']
CHECKMARK_COLUMN = 'P'

# Folder structure
BASE_FOLDER = "/Users/ikeyike/Desktop/the_shop_inventory/organized_images"
ARCHIVE_DIR = "/Users/ikeyike/Desktop/the_shop_inventory/archive"
UPLOAD_LOG = "/Users/ikeyike/Desktop/the_shop_inventory/uploaded_to_sheet_log.csv"

# Google Drive parent folder ID
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")


def get_uploaded_folders():
    if not os.path.exists(UPLOAD_LOG):
        return set()
    with open(UPLOAD_LOG, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        return set(row[1] for row in reader if row[5] == "Uploaded")


def authenticate_google_services():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return sheets_service, drive_service


def log_to_sheet_upload_log(folder_name, toy_number, variant, status, image_files=None):
    log_exists = os.path.isfile(UPLOAD_LOG)
    with open(UPLOAD_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        if not log_exists:
            writer.writerow(["timestamp", "folder_name", "toy_number", "variant", "image_filepaths", "status"])
        image_paths = "; ".join(image_files) if image_files else ""
        writer.writerow([datetime.now().isoformat(), folder_name, toy_number, variant, image_paths, status])


def mark_as_uploaded(sheet_service, row_index):
    update_range = f"{SHEET_NAME}!{CHECKMARK_COLUMN}{row_index}"
    body = {"values": [["✔"]]}
    sheet_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=update_range,
        valueInputOption="RAW",
        body=body
    ).execute()


def get_or_create_drive_subfolder(drive_service, parent_folder_id, folder_name):
    query = (
        f"'{parent_folder_id}' in parents and "
        f"name = '{folder_name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )

    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = response.get('files', [])

    if folders:
        return folders[0]['id']

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }

    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    return folder['id']


def upload_to_drive(drive_service, file_path, destination_folder_id, retries=3):
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name, 'parents': [destination_folder_id]}
    media = MediaFileUpload(file_path, resumable=False)

    for attempt in range(1, retries + 1):
        try:
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')

            drive_service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()

            return f"https://drive.google.com/uc?id={file_id}"

        except Exception as e:
            print(f"⚠️ Upload failed for {file_name} (attempt {attempt}): {e}")
            if attempt < retries:
                time.sleep(2 * attempt)  # exponential backoff
            else:
                raise


def update_sheet_with_links(sheets_service, toy_number, variant, image_links):
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!{ID_COLUMN}:{CHECKMARK_COLUMN}"
    ).execute()
    values = result.get('values', [])

    for idx, row in enumerate(values):
        if len(row) > VARIANT_COLUMN_INDEX and row[0] == toy_number and row[VARIANT_COLUMN_INDEX] == variant:
            row_index = idx + 1
            data = [{
                'range': f"{SHEET_NAME}!{col}{row_index}",
                'values': [[image_links[i]] if i < len(image_links) else [""]]
            } for i, col in enumerate(IMAGE_COLUMNS)]
            sheet.values().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body={'valueInputOption': 'USER_ENTERED', 'data': data}
            ).execute()
            mark_as_uploaded(sheets_service, row_index)
            print(f"✅ Updated row {row_index} for {toy_number} - {variant}")
            return True

    print(f"⚠️ Entry not found for {toy_number} - {variant}.")
    return False


def process_images(folder_path, sheets_service, drive_service, folder_name, uploaded_folders):
    if folder_name in uploaded_folders:
        print(f"⏩ Skipping {folder_name} (already uploaded)")
        return

    toy_number = folder_name.split('-')[0]
    variant = folder_name.split('-')[1] if '-' in folder_name else ""
    image_files = sorted(glob.glob(os.path.join(folder_path, '*.*')))
    image_filenames = [os.path.basename(f) for f in image_files]

    if not image_files:
        print(f"⚠️ No images found in {folder_path}")
        log_to_sheet_upload_log(folder_name, toy_number, variant, "No Images", image_filenames)
        return

    try:
        drive_subfolder_id = get_or_create_drive_subfolder(drive_service, DRIVE_FOLDER_ID, folder_name)
        image_links = [upload_to_drive(drive_service, img, drive_subfolder_id) for img in image_files]
    except Exception as e:
        print(f"❌ Upload to Drive failed: {e}")
        log_to_sheet_upload_log(folder_name, toy_number, variant, "Drive Upload Error", image_filenames)
        return

    update_success = update_sheet_with_links(sheets_service, toy_number, variant, image_links)
    log_to_sheet_upload_log(folder_name, toy_number, variant, "Uploaded" if update_success else "Sheet Update Error", image_filenames)

    if update_success and ARCHIVE_ENABLED:
        box_name = os.path.basename(os.path.dirname(folder_path))
        archive_box_path = os.path.join(ARCHIVE_DIR, box_name)
        os.makedirs(archive_box_path, exist_ok=True)
        shutil.move(folder_path, os.path.join(archive_box_path, folder_name))
        print(f"📦 Archived {folder_name} under {box_name}")
    elif update_success:
        print(f"✅ Upload success. Archive skipped (ARCHIVE_ENABLED=False)")
    else:
        print(f"⚠️ Retaining folder due to upload error: {folder_name}")


def main():
    sheets_service, drive_service = authenticate_google_services()
    uploaded_folders = get_uploaded_folders()

    for box_folder in os.listdir(BASE_FOLDER):
        box_path = os.path.join(BASE_FOLDER, box_folder)
        if not os.path.isdir(box_path):
            continue

        print(f"📦 Scanning box: {box_folder}")
        for folder_name in os.listdir(box_path):
            folder_path = os.path.join(box_path, folder_name)
            if os.path.isdir(folder_path):
                print(f"➡️ Processing folder: {folder_name}")
                process_images(folder_path, sheets_service, drive_service, folder_name, uploaded_folders)


if __name__ == "__main__":
    main()