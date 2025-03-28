
import os
import glob
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = '2008HotWheels'
ID_COLUMN = 'A'
IMAGE_COLUMNS = ['M', 'N', 'O', 'P', 'Q']  # Photo links start at column M (after your existing columns A–L)

def authenticate_google_services():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return sheets_service, drive_service

def upload_images_to_drive(drive_service, folder_path):
    links = []
    image_files = sorted(glob.glob(os.path.join(folder_path, '*.*')))
    for image_file in image_files:
        file_metadata = {'name': os.path.basename(image_file)}
        media = MediaFileUpload(image_file, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        drive_service.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()
        sharable_link = f"https://drive.google.com/uc?id={file_id}"
        links.append(sharable_link)
    return links

def update_sheet_with_links(sheets_service, product_id, image_links):
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!{ID_COLUMN}:{ID_COLUMN}").execute()
    values = result.get('values', [])
    for idx, row in enumerate(values):
        if row and row[0] == product_id:
            row_index = idx + 1
            updates = [[link] for link in image_links]
            data = [{
                'range': f"{SHEET_NAME}!{col}{row_index}",
                'values': [updates[i]] if i < len(updates) else [[""]]
            } for i, col in enumerate(IMAGE_COLUMNS)]
            body = {'valueInputOption': 'USER_ENTERED', 'data': data}
            sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
            print(f"Updated row {row_index} for product {product_id}")
            return
    print(f"Product ID {product_id} not found in column {ID_COLUMN}.")

if __name__ == "__main__":
    product_id = input("Enter product identifier (e.g., M6916-0918K): ").strip()
    folder_path = os.path.join("/Users/naomiabella/Desktop/TheShopInventory/OrganizedImages", product_id)
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        exit(1)

    sheets_service, drive_service = authenticate_google_services()
    links = upload_images_to_drive(drive_service, folder_path)
    update_sheet_with_links(sheets_service, product_id, links)


