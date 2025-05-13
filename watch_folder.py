#!/usr/bin/env python3

import os
import time
import subprocess
import shutil
from shutil import move

# Paths and Configurations
WATCH_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
PROCESSED_LOG = "processed_images.csv"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
OCR_SCRIPT = "ocr_batch_google.py"
SHEETS_SCRIPT = "google_sheets_linker.py"
AUTO_RUN_SHEETS = False
TESTING_MODE = True

def load_processed_images():
    """Load paths of already processed images to avoid reprocessing."""
    if not os.path.exists(PROCESSED_LOG):
        return set()
    with open(PROCESSED_LOG, "r") as f:
        return set(line.strip().split(",")[0] for line in f.readlines())

def log_processed_image(image_path, toy_number, variant, status):
    """Log processed images with their status."""
    with open(PROCESSED_LOG, "a") as f:
        f.write(f"{image_path},{toy_number},{variant},{status}\n")

def get_new_images(processed):
    """Get unprocessed images from the watch folder."""
    all_images = sorted([
        os.path.join(WATCH_FOLDER, f)
        for f in os.listdir(WATCH_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic"))
    ])
    return [img for img in all_images if img not in processed]

def process_batch(front_img, back_img):
    """Process a pair of images - front and back."""
    try:
        print(f"📸 Processing batch: {front_img}, {back_img}")
        subprocess.run(["python3", OCR_SCRIPT, front_img, back_img], check=True)
        print(f"✅ Successfully processed batch: {front_img}, {back_img}")
    except Exception as e:
        print(f"⚠️ Error processing batch: {e}")
        handle_ocr_failure([front_img, back_img])

def handle_ocr_failure(batch):
    """Handle OCR failures by moving images to the unmatched folder."""
    print("⚠️ OCR failed. Moving to unmatched folder.")
    for img in batch:
        target_path = os.path.join(UNMATCHED_FOLDER, os.path.basename(img))
        if TESTING_MODE:
            shutil.copy(img, target_path)
        else:
            shutil.move(img, target_path)
        log_processed_image(img, "NA", "NA", "Unmatched")
    print("🟡 Please run multi_image_renamer.py manually on unmatched images.")

def run_google_sheets_linker():
    """Run the Google Sheets linker script to update the sheet with image paths."""
    print("🔗 Updating Google Sheets...")
    try:
        subprocess.run(["python3", SHEETS_SCRIPT], check=True)
        print("✅ Google Sheets update complete.")
    except Exception as e:
        print(f"⚠️ Sheets update failed: {e}")

def main():
    """Main loop to monitor the watch folder and process images in pairs."""
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    print("👀 Watching for new image pairs...")

    while True:
        try:
            processed = load_processed_images()
            new_images = get_new_images(processed)

            # Process in batches of 2
            if len(new_images) >= 2:
                batch = new_images[:2]
                front_img, back_img = batch

                # Ensure order of processing: Front first, Back second
                process_batch(front_img, back_img)

                # Delete processed images
                for img in batch:
                    if os.path.exists(img):
                        os.remove(img)
                        print(f"🗑️ Deleted: {img}")

                # Run Google Sheets linker if enabled
                if AUTO_RUN_SHEETS:
                    run_google_sheets_linker()

            # Wait before next check
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n🛑 Watcher stopped manually.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
