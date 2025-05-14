import os
import re
import shutil
from google.cloud import vision
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

TESTING_MODE = True  # Toggle to prevent deletion of source images during testing

# Configuration
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_vision_key.json"

WATCH_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
OUTPUT_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/organized_images"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
LOG_FILE = "/Users/naomiabella/Desktop/the_shop_inventory/processed_images.csv"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '135derlsER5TZEdZ7kEIJQQ1G1Z6thpZfydFsnqkb9EM'
SHEET_NAME = 'Inventory'
TOY_COLUMN = 'A'
VARIANT_COLUMN = 'M'

client = vision.ImageAnnotatorClient()

def log_processed_image(file_path, identifier, status):
    """Log processed images with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp},{file_path},{identifier},{status}\n")

def is_first_duplicate(identifier):
    """Check if an identifier has been logged as a duplicate before."""
    try:
        with open(LOG_FILE, "r") as log_file:
            for line in log_file:
                parts = line.strip().split(',')
                if len(parts) < 4:
                    continue
                _, _, logged_identifier, status = parts
                if logged_identifier == identifier and status == "Duplicate":
                    return False
    except FileNotFoundError:
        open(LOG_FILE, "a").close()

    return True

def is_duplicate(identifier):
    """Check if the identifier has already been processed."""
    try:
        with open(LOG_FILE, "r") as log_file:
            for line in log_file:
                parts = line.strip().split(',')
                if len(parts) < 4:
                    continue
                _, _, logged_identifier, status = parts
                if logged_identifier == identifier and status == "Processed":
                    return True
    except FileNotFoundError:
        open(LOG_FILE, "a").close()

    return False

def authenticate_google_sheets():
    """Authenticate and return Google Sheets service."""
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        print("✅ Google Sheets authenticated.")
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        print(f"⚠️ Error authenticating Google Sheets: {e}")
        return None

def get_variant_from_sheet(sheets_service, toy_number):
    """Fetch the variant from Google Sheets based on the Toy #."""
    try:
        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!{TOY_COLUMN}:{VARIANT_COLUMN}"
        ).execute()

        values = result.get('values', [])
        for row in values:
            if row and len(row) >= 13 and row[0] == toy_number:
                variant = row[12].strip() if row[12] else ""
                print(f"✅ Google Sheets Variant for {toy_number}: {variant}")
                return variant

        print(f"⚠️ No Variant found in Google Sheets for Toy #: {toy_number}")
    except Exception as e:
        print(f"⚠️ Error accessing Google Sheets: {e}")

    return ""

def extract_toy_number(text):
    """Extract Toy # from the OCR text."""
    match = re.search(r"\b([A-Z0-9]{5})[-]([A-Z0-9]{4,5})\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else None

def ocr_text_from_image(image_path):
    """Extract Toy # from the back image using Google Vision."""
    try:
        with open(image_path, "rb") as img_file:
            content = img_file.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.text_annotations:
            extracted_text = response.full_text_annotation.text
            toy_number = extract_toy_number(extracted_text)
            return toy_number

    except Exception as e:
        print(f"⚠️ Error during OCR for {image_path}: {e}")
    
    return None

def process_batch(images, sheets_service):
    """Process a batch of images to extract Toy # and move accordingly."""
    print(f"📸 Processing batch: {images}")

    if len(images) != 2:
        print(f"⚠️ Incomplete batch detected: {images}")
        return

    front_image, back_image = images
    toy_number = ocr_text_from_image(back_image)

    if toy_number:
        variant = get_variant_from_sheet(sheets_service, toy_number)
        identifier = f"{toy_number}-{variant}" if variant else toy_number

        # Check for duplicates
        if is_duplicate(identifier):
            if is_first_duplicate(identifier):
                print(f"⚠️ First Duplicate Detected for {identifier}")
                log_processed_image("N/A", identifier, "Duplicate")
            else:
                print(f"⚠️ Duplicate (Not Logged) for {identifier}")
            return

        # Construct target folder path
        target_folder = os.path.join(OUTPUT_FOLDER, identifier)
        os.makedirs(target_folder, exist_ok=True)

        for i, img_path in enumerate(images):
            new_name = f"{identifier}_{i + 1}.jpg"
            dest_path = os.path.join(target_folder, new_name)
            print(f"✅ Moving {img_path} to {dest_path}")

            try:
                if TESTING_MODE:
                    shutil.copy(img_path, dest_path)
                else:
                    shutil.move(img_path, dest_path)

                log_processed_image(dest_path, identifier, "Processed")

            except Exception as e:
                print(f"⚠️ Error moving {img_path}: {e}")
                log_processed_image(img_path, "Unknown", "Error")

    else:
        print("⚠️ No Toy # detected. Moving to unmatched folder.")
        for img in images:
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, os.path.basename(img))
            try:
                if TESTING_MODE:
                    shutil.copy(img, unmatched_dest)
                else:
                    shutil.move(img, unmatched_dest)
                log_processed_image(unmatched_dest, "Unknown", "Unmatched")
            except Exception as e:
                print(f"⚠️ Error moving to unmatched: {e}")

def main():
    print("Starting ocr_batch_google.py...")
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    sheets_service = authenticate_google_sheets()
    if not sheets_service:
        print("⚠️ Google Sheets authentication failed. Exiting.")
        return

    try:
        files = sorted([
            os.path.join(WATCH_FOLDER, f) for f in os.listdir(WATCH_FOLDER)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')) and not f.startswith('.') and f.lower() != "icon"
        ])

        for i in range(0, len(files), 2):
            batch = files[i:i + 2]
            process_batch(batch, sheets_service)

    except Exception as e:
        print(f"⚠️ Error in main processing loop: {e}")

if __name__ == "__main__":
    main()
