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
    """Authenticate and return Google Sheets service."""
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        print("✅ Google Sheets authenticated.")
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        print(f"⚠️ Error authenticating Google Sheets: {e}")
        return None

def log_processed_image(image_path, toy_number, variant, status):
    """Log processed images with [Image Path, Toy #, Variant, Status]."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{image_path},{toy_number},{variant},{status}\n")

def is_duplicate(toy_number, variant):
    """Check if the Toy # and Variant are already logged as 'Processed'."""
    try:
        with open(LOG_FILE, "r") as log_file:
            for line in log_file:
                _, logged_toy_number, logged_variant, status = line.strip().split(',')
                if logged_toy_number == toy_number and logged_variant == variant and status == "Processed":
                    print(f"⚠️ Duplicate detected for {toy_number} - {variant}")
                    return True
    except FileNotFoundError:
        open(LOG_FILE, "a").close()

    return False

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
    """Extract the Toy # from the OCR text."""
    match = re.search(r"\b([A-Z0-9]{5})[-][A-Z0-9]{4,5}\b", text, re.IGNORECASE)
    return match.group(1) if match else None

def ocr_text_from_image(image_path):
    """Extract Toy # from the back image using Google Vision."""
    try:
        with open(image_path, "rb") as img_file:
            content = img_file.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if not response.text_annotations:
            print(f"⚠️ No text detected in {image_path}")
            return ""

        extracted_text = response.full_text_annotation.text
        toy_number = extract_toy_number(extracted_text)
        
        if toy_number:
            print(f"✅ Extracted Toy Number: {toy_number}")
        else:
            print(f"⚠️ No Toy # found in {image_path}")

        return toy_number

    except Exception as e:
        print(f"⚠️ Error during OCR for {image_path}: {e}")
        return ""

def process_batch(images, sheets_service):
    """Process a batch of images to extract Toy # and move accordingly."""
    print(f"📸 Processing batch: {images}")

    if len(images) != 2:
        print("⚠️ Incomplete batch detected. Skipping.")
        return

    front_image, back_image = images

    # Extract Toy # from the back image
    toy_number = ocr_text_from_image(back_image)

    if toy_number:
        # Get Variant from Google Sheets
        variant = get_variant_from_sheet(sheets_service, toy_number)
        
        # Check for duplicates
        if is_duplicate(toy_number, variant):
            for img in images:
                log_processed_image(img, toy_number, variant, "Duplicate")
            return

        # Proceed with processing
        folder_name = f"{toy_number}-{variant}" if variant else toy_number
        target_folder = os.path.join(OUTPUT_FOLDER, folder_name)
        os.makedirs(target_folder, exist_ok=True)

        for i, img_path in enumerate(images):
            new_name = f"{toy_number}_{i + 1}.jpg"
            dest_path = os.path.join(target_folder, new_name)
            print(f"✅ Moving {img_path} to {dest_path}")

            try:
                if TESTING_MODE:
                    shutil.copy(img_path, dest_path)
                else:
                    shutil.move(img_path, dest_path)

                log_processed_image(dest_path, toy_number, variant, "Processed")
            except Exception as e:
                print(f"⚠️ Error moving {img_path}: {e}")
                log_processed_image(img_path, toy_number, variant, "Error")
    else:
        print("⚠️ No Toy # detected. Moving to unmatched folder.")
        for img in images:
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, os.path.basename(img))
            try:
                if TESTING_MODE:
                    shutil.copy(img, unmatched_dest)
                else:
                    shutil.move(img, unmatched_dest)

                log_processed_image(unmatched_dest, "Unknown", "Unknown", "Unmatched")
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
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))
        ])
        print(f"Files found for processing: {files}")

        for i in range(0, len(files), 2):
            batch = files[i:i + 2]
            process_batch(batch, sheets_service)

    except Exception as e:
        print(f"⚠️ Error in main processing loop: {e}")

if __name__ == "__main__":
    main()
