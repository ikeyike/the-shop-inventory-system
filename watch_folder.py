#!/usr/bin/env python3

import os
import time
import subprocess

# Paths and Configurations
WATCH_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
OCR_SCRIPT = "ocr_batch_google.py"
AUTO_RUN_SHEETS = False

def get_new_images():
    # Get images from the watch folder
    all_images = sorted([
        os.path.join(WATCH_FOLDER, f)
        for f in os.listdir(WATCH_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic"))
    ])
    return all_images

def process_batch(front_img, back_img):
    # Pass the image pair to ocr_batch_google.py for processing
    try:
        print(f"📸 Processing batch: {front_img}, {back_img}")
        subprocess.run(["python3", OCR_SCRIPT, front_img, back_img], check=True)
        print(f"✅ Successfully processed batch: {front_img}, {back_img}")
    except Exception as e:
        print(f"⚠️ Error processing batch: {e}")

def main():
    # Main loop to monitor the watch folder and pass image pairs to ocr_batch_google.py
    print("👀 Watching for new image pairs...")

    while True:
        try:
            new_images = get_new_images()

            # Process in batches of 2
            while len(new_images) >= 2:
                front_img, back_img = new_images[:2]
                process_batch(front_img, back_img)

                # Remove processed images
                os.remove(front_img)
                os.remove(back_img)

                # Update the image list
                new_images = get_new_images()

            time.sleep(5)

        except KeyboardInterrupt:
            print("Watcher stopped manually.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
