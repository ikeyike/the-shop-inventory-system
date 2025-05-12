import os
import re
import shutil
from google.cloud import vision

# Configuration
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_vision_key.json"
TESTING_MODE = True  # Toggle to prevent deletion of source images during testing

WATCH_FOLDER = "/Users/yourusername/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
OUTPUT_FOLDER = "/Users/yourusername/Desktop/the_shop_inventory/organized_images"
UNMATCHED_FOLDER = "/Users/yourusername/Desktop/the_shop_inventory/unmatched"
LOG_FILE = "processed_images.csv"

# OCR Client
client = vision.ImageAnnotatorClient()

def extract_toy_number(text):
    """Extract the Toy # (e.g., M6916) from the OCR text."""
    match = re.search(r"\b([A-Z0-9]{5})[-][A-Z0-9]{4,5}\b", text, re.IGNORECASE)
    return match.group(1) if match else None

def ocr_text_from_image(image_path):
    """Run OCR on the image to extract text."""
    with open(image_path, "rb") as img_file:
        content = img_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.full_text_annotation.text if response.text_annotations else ""

def log_processed_image(image_path, toy_number, variant, status):
    """Log the processed image information."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{image_path},{toy_number},{variant},{status}\n")

def move_images(images, toy_number, variant):
    """Move images to organized folder or unmatched folder based on OCR success."""
    folder_name = f"{toy_number}-{variant}"
    target_folder = os.path.join(OUTPUT_FOLDER, folder_name)
    os.makedirs(target_folder, exist_ok=True)

    for i, img_path in enumerate(images):
        new_name = f"{toy_number}_{i + 1}.jpg"
        dest_path = os.path.join(target_folder, new_name)

        try:
            if TESTING_MODE:
                shutil.copy(img_path, dest_path)  # Copy instead of move
                print(f"[TEST MODE] Copied {img_path} to {dest_path}")
            else:
                shutil.move(img_path, dest_path)  # Move in non-testing mode
                print(f"✅ Moved {img_path} to {dest_path}")

            log_processed_image(dest_path, toy_number, variant, "Processed")

        except Exception as e:
            print(f"⚠️ Error moving image {img_path}: {e}")
            log_processed_image(img_path, toy_number, variant, "Error")

def process_batch(images):
    """Process a batch of images and log results."""
    texts = [ocr_text_from_image(img) for img in images]
    toy_numbers = [extract_toy_number(text) for text in texts]

    for toy_number in toy_numbers:
        if toy_number:
            # Placeholder for variant logic if needed in the future
            variant = "Default"
            move_images(images, toy_number, variant)
            return

    # If no toy number is found
    print("⚠️ No valid Toy # detected. Moving to unmatched folder.")
    for img in images:
        unmatched_dest = os.path.join(UNMATCHED_FOLDER, os.path.basename(img))
        if TESTING_MODE:
            shutil.copy(img, unmatched_dest)
            print(f"[TEST MODE] Copied to unmatched: {unmatched_dest}")
        else:
            shutil.move(img, unmatched_dest)
            print(f"Moved to unmatched: {unmatched_dest}")

        log_processed_image(unmatched_dest, "Unknown", "Unknown", "Unmatched")

def main():
    files = sorted([os.path.join(WATCH_FOLDER, f) for f in os.listdir(WATCH_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))])

    for i in range(0, len(files), 2):
        batch = files[i:i + 2]
        if len(batch) == 2:
            print(f"📸 Processing batch: {batch}")
            process_batch(batch)
        else:
            print(f"⚠️ Incomplete batch: {batch}")

if __name__ == "__main__":
    main()
