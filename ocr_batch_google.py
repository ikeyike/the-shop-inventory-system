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

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'
TOY_COLUMN = 'A'
VARIANT_COLUMN = 'M'

# Initialize the Google Vision Client
client = vision.ImageAnnotatorClient()

def authenticate_google_sheets():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def get_variant_from_sheet(sheets_service, toy_number):
    """Fetch the variant from Google Sheets based on the Toy #."""
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=f"{SHEET_NAME}!{TOY_COLUMN}:{VARIANT_COLUMN}"
    ).execute()

    values = result.get('values', [])
    for row in values:
        if row and len(row) >= 13 and row[0] == toy_number:
            variant = row[12].strip() if row[12] else ""
            print(f"Google Sheets Variant for {toy_number}: {variant}")
            return variant
    print(f"No Variant found in Google Sheets for Toy #: {toy_number}")
    return ""

def extract_toy_number(text):
    """Extract the Toy # from the OCR text."""
    match = re.search(r"\b([A-Z0-9]{5})[-][A-Z0-9]{4,5}\b", text, re.IGNORECASE)
    toy_number = match.group(1) if match else None
    print(f"Extracted Toy Number: {toy_number}")
    return toy_number

def ocr_text_from_image(image_path):
    """Extract text using Google Vision."""
    with open(image_path, "rb") as img_file:
        content = img_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.full_text_annotation.text if response.text_annotations else ""

def log_processed_image(image_path, toy_number, variant, status):
    """Log processed images with [Image Path, Toy #, Variant, Status]."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{image_path},{toy_number},{variant},{status}\n")

def move_images(images, toy_number, variant):
    """Move images to the organized folder and log the actions."""
    folder_name = f"{toy_number}" if not variant else f"{toy_number}-{variant}"
    target_folder = os.path.join(OUTPUT_FOLDER, folder_name)
    os.makedirs(target_folder, exist_ok=True)

    for i, img_path in enumerate(images):
        new_name = f"{toy_number}_{i + 1}.jpg"
        dest_path = os.path.join(target_folder, new_name)

        try:
            # Copy or Move based on TESTING_MODE
            if TESTING_MODE:
                shutil.copy(img_path, dest_path)
            else:
                shutil.move(img_path, dest_path)
                
            log_processed_image(dest_path, toy_number, variant, "Processed")
            print(f"✅ Processed and logged: {img_path} -> {dest_path}")

        except Exception as e:
            print(f"⚠️ Error processing image {img_path}: {e}")
            log_processed_image(img_path, toy_number, variant, "Error")

def process_batch(images, sheets_service):
    """Process a batch of images to extract Toy # and move accordingly."""
    texts = [ocr_text_from_image(img) for img in images]
    toy_numbers = [extract_toy_number(text) for text in texts]

    for toy_number in toy_numbers:
        if toy_number:
            variant = get_variant_from_sheet(sheets_service, toy_number)
            move_images(images, toy_number, variant)
            return

    # Handle unmatched images
    print("⚠️ No valid Toy # detected. Moving to unmatched folder.")
    for img in images:
        unmatched_dest = os.path.join(UNMATCHED_FOLDER, os.path.basename(img))
        
        # Copy or Move based on TESTING_MODE
        if TESTING_MODE:
            shutil.copy(img, unmatched_dest)
        else:
            shutil.move(img, unmatched_dest)
        
        log_processed_image(unmatched_dest, "Unknown", "Unknown", "Unmatched")

def main():
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    sheets_service = authenticate_google_sheets()

    # Collect images from the watch folder
    files = sorted([
        os.path.join(WATCH_FOLDER, f) for f in os.listdir(WATCH_FOLDER) 
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))
    ])

    # Process in batches of 2
    for i in range(0, len(files), 2):
        batch = files[i:i + 2]
        if len(batch) == 2:
            print(f"📸 Processing batch: {batch}")
            process_batch(batch, sheets_service)
        else:
            print(f"⚠️ Incomplete batch: {batch}")

if __name__ == "__main__":
    main()
