import os
import re
import shutil
from google.cloud import vision
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

# Toggle to prevent deletion of source images during testing
TESTING_MODE = True

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

# Ensure log file has headers
def ensure_log_headers():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        with open(LOG_FILE, "w") as log_file:
            log_file.write("Timestamp,File Path,Original Name,Identifier,Status\n")

# Log processed images with timestamp
def log_processed_image(file_path, original_name, identifier, status):
    ensure_log_headers()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp},{file_path},{original_name},{identifier},{status}\n")

# Check if the identifier has already been processed
def is_duplicate(identifier):
    try:
        with open(LOG_FILE, "r") as log_file:
            for line in log_file:
                parts = line.strip().split(',')
                if len(parts) >= 5 and parts[3] == identifier and parts[4] == "Processed":
                    return True
    except FileNotFoundError:
        open(LOG_FILE, "a").close()
    return False

# Extract Toy # from the OCR text (Only the part left of the dash)
def extract_toy_number(text):
    match = re.search(r"\b([A-Z0-9]{5})[-][A-Z0-9]{4,5}\b", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    else:
        print(f"⚠️ Invalid Identifier Detected: {text.strip()}")
        log_processed_image("N/A", "N/A", text.strip(), "Invalid")
        return None

# Extract Toy # from the back image using Google Vision
def ocr_text_from_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            content = img_file.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.text_annotations:
            extracted_text = response.full_text_annotation.text.strip()
            toy_number = extract_toy_number(extracted_text)
            if toy_number:
                print(f"✅ Extracted Toy Number: {toy_number}")
                return toy_number

    except Exception as e:
        print(f"⚠️ Error during OCR for {image_path}: {e}")
    
    print(f"⚠️ No valid Toy # found in {image_path}")
    return None

# Authenticate and return Google Sheets service
def authenticate_google_sheets():
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        print("✅ Google Sheets authenticated.")
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        print(f"⚠️ Error authenticating Google Sheets: {e}")
        return None

# Fetch variant from Google Sheets based on Toy #
def get_variant_from_sheet(sheets_service, toy_number):
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
                print(f"✅ Matched Variant for {toy_number}: {variant}")
                return variant

    except Exception as e:
        print(f"⚠️ Error accessing Google Sheets: {e}")

    return ""

# Process a batch of images to extract Toy # and move accordingly
def process_batch(images, sheets_service):
    print(f"📸 Processing batch: {images}")

    if len(images) != 2:
        print(f"⚠️ Incomplete batch detected: {images}")
        return

    front_image, back_image = images
    front_original_name = os.path.basename(front_image)
    back_original_name = os.path.basename(back_image)

    toy_number = ocr_text_from_image(back_image)

    if toy_number:
        # Check for duplicates - only show in console, do not log
        if is_duplicate(toy_number):
            print(f"⚠️ Duplicate (Not Logged) for {toy_number}")
            return

        variant = get_variant_from_sheet(sheets_service, toy_number)
        identifier = toy_number

        # Create target folder path
        target_folder = os.path.join(OUTPUT_FOLDER, identifier)
        os.makedirs(target_folder, exist_ok=True)

        # Move images to target folder
        for i, (img_path, original_name) in enumerate([(front_image, front_original_name), (back_image, back_original_name)]):
            new_name = f"{identifier}_{i + 1}.jpg"
            dest_path = os.path.join(target_folder, new_name)
            print(f"✅ Moving {img_path} to {dest_path}")

            try:
                if TESTING_MODE:
                    shutil.copy(img_path, dest_path)
                else:
                    shutil.move(img_path, dest_path)

                log_processed_image(dest_path, original_name, identifier, "Processed")

            except Exception as e:
                print(f"⚠️ Error moving {img_path}: {e}")
                log_processed_image(img_path, original_name, "Unknown", "Error")

    else:
        print("⚠️ No Toy # detected. Moving to unmatched folder.")
        for img in images:
            original_name = os.path.basename(img)
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, original_name)
            try:
                if TESTING_MODE:
                    shutil.copy(img, unmatched_dest)
                else:
                    shutil.move(img, unmatched_dest)

                log_processed_image(unmatched_dest, original_name, "Unknown", "Unmatched")

            except Exception as e:
                print(f"⚠️ Error moving to unmatched: {e}")

# Process images in the watch folder in pairs
def process_images(sheets_service):
    files = sorted([
        os.path.join(WATCH_FOLDER, f) for f in os.listdir(WATCH_FOLDER)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')) and not f.startswith('.') and f.lower() != "icon"
    ])

    for i in range(0, len(files), 2):
        batch = files[i:i + 2]
        if len(batch) == 2:
            process_batch(batch, sheets_service)

def main():
    print("Starting OCR Batch Processing...")
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    sheets_service = authenticate_google_sheets()

    if sheets_service:
        process_images(sheets_service)

if __name__ == "__main__":
    main()
