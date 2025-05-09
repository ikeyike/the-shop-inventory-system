import os
import re
import shutil
from google.cloud import vision
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_vision_key.json"

WATCH_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
OUTPUT_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/organized_images"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
LOG_FILE = "processed_images.csv"

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'
TOY_COLUMN = 'A'
VARIANT_COLUMN = 'M'

def authenticate_google_sheets():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def get_variant_from_sheet(sheets_service, toy_number):
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=f"{SHEET_NAME}!{TOY_COLUMN}:{VARIANT_COLUMN}"
    ).execute()

    values = result.get('values', [])
    for row in values:
        if row and len(row) >= 2 and row[0] == toy_number:
            return row[1]
    return "Unknown"

def extract_toy_number(text):
    match = re.search(r"\b([A-Z0-9]{5})[-][A-Z0-9]{4,5}\b", text, re.IGNORECASE)
    return match.group(1) if match else None

def ocr_text_from_image(image_path):
    with open(image_path, "rb") as img_file:
        content = img_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.full_text_annotation.text if response.text_annotations else ""

def log_processed_image(image_path, toy_number, variant, status):
    with open(LOG_FILE, "a") as f:
        f.write(f"{image_path},{toy_number},{variant},{status}\n")

def move_images(images, toy_number, variant):
    folder_name = f"{toy_number}-{variant}"
    target_folder = os.path.join(OUTPUT_FOLDER, folder_name)
    os.makedirs(target_folder, exist_ok=True)

    for i, img_path in enumerate(images):
        new_name = f"{toy_number}_{i + 1}.jpg"
        dest_path = os.path.join(target_folder, new_name)

        try:
            shutil.move(img_path, dest_path)
            log_processed_image(dest_path, toy_number, variant, "Processed")
            print(f"✅ Moved {img_path} to {dest_path}")
        except Exception as e:
            print(f"⚠️ Error moving image {img_path}: {e}")
            log_processed_image(img_path, toy_number, variant, "Error")

def process_batch(images, sheets_service):
    texts = [ocr_text_from_image(img) for img in images]
    toy_numbers = [extract_toy_number(text) for text in texts]

    for toy_number in toy_numbers:
        if toy_number:
            variant = get_variant_from_sheet(sheets_service, toy_number)
            move_images(images, toy_number, variant)
            return

    print("⚠️ No valid Toy # detected. Moving to unmatched folder.")
    for img in images:
        unmatched_dest = os.path.join(UNMATCHED_FOLDER, os.path.basename(img))
        shutil.move(img, unmatched_dest)
        log_processed_image(unmatched_dest, "Unknown", "Unknown", "Unmatched")

def main():
    sheets_service = authenticate_google_sheets()

    files = sorted([os.path.join(WATCH_FOLDER, f) for f in os.listdir(WATCH_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))])

    for i in range(0, len(files), 2):
        batch = files[i:i + 2]
        if len(batch) == 2:
            print(f"📸 Processing batch: {batch}")
            process_batch(batch, sheets_service)
        else:
            print(f"⚠️ Incomplete batch: {batch}")

if __name__ == "__main__":
    main()
