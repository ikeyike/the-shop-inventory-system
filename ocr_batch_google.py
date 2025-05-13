import os
import re
import shutil
from google.cloud import vision
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

TESTING_MODE = True  # Toggle to prevent deletion of source images during testing

# Configuration
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_vision_key.json"

WATCH_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
OUTPUT_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/organized_images"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
LOG_FILE = "processed_images.csv"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'
TOY_COLUMN = 'A'
VARIANT_COLUMN = 'M'

client = vision.ImageAnnotatorClient()

def authenticate_google_sheets():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def log_processed_image(image_path, toy_number, variant, status):
    with open(LOG_FILE, "a") as f:
        f.write(f"{image_path},{toy_number},{variant},{status}\n")

def is_duplicate(image_path):
    with open(LOG_FILE, "r") as f:
        return any(image_path in line for line in f)

def get_variant_from_sheet(sheets_service, toy_number):
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!{TOY_COLUMN}:{VARIANT_COLUMN}"
    ).execute()

    values = result.get('values', [])
    for row in values:
        if row and len(row) >= 13 and row[0] == toy_number:
            return row[12].strip() if row[12] else ""
    return ""

def extract_toy_number(text):
    match = re.search(r"\b([A-Z0-9]{5})[-]([A-Z0-9]{4,5})\b", text, re.IGNORECASE)
    return match.group(1) if match else None

def ocr_text_from_image(image_path):
    with open(image_path, "rb") as img_file:
        content = img_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.full_text_annotation.text if response.text_annotations else ""

def process_batch(images, sheets_service):
    if len(images) != 2:
        return

    front_image, back_image = images

    if is_duplicate(front_image) or is_duplicate(back_image):
        log_processed_image(front_image, "Unknown", "Unknown", "Duplicate")
        log_processed_image(back_image, "Unknown", "Unknown", "Duplicate")
        return

    text_back = ocr_text_from_image(back_image)
    toy_number = extract_toy_number(text_back)

    if toy_number:
        variant = get_variant_from_sheet(sheets_service, toy_number)
        folder_name = f"{toy_number}-{variant}" if variant else toy_number
        target_folder = os.path.join(OUTPUT_FOLDER, folder_name)
        os.makedirs(target_folder, exist_ok=True)

        for i, img_path in enumerate(images):
            new_name = f"{toy_number}_{i + 1}.jpg"
            dest_path = os.path.join(target_folder, new_name)

            if TESTING_MODE:
                shutil.copy(img_path, dest_path)
            else:
                shutil.move(img_path, dest_path)

            log_processed_image(dest_path, toy_number, variant, "Processed")
    else:
        for img in images:
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, os.path.basename(img))
            if TESTING_MODE:
                shutil.copy(img, unmatched_dest)
            else:
                shutil.move(img, unmatched_dest)

            log_processed_image(unmatched_dest, "Unknown", "Unknown", "Unmatched")

def main():
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    sheets_service = authenticate_google_sheets()

    files = sorted([
        os.path.join(WATCH_FOLDER, f) for f in os.listdir(WATCH_FOLDER)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))
    ])

    for i in range(0, len(files), 2):
        batch = files[i:i + 2]
        if len(batch) == 2:
            process_batch(batch, sheets_service)

if __name__ == "__main__":
    main()
