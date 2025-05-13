#!/usr/bin/env python3

import os
import time
import subprocess

# Paths and Configurations
WATCH_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
OCR_SCRIPT = "ocr_batch_google.py"

SYNC_CHECKS = 3  # Number of consecutive checks for file size stability
SYNC_WAIT_TIME = 5  # Time to wait between checks (in seconds)

def get_new_images():
    # Get images from the watch folder
    all_images = sorted([
        os.path.join(WATCH_FOLDER, f)
        for f in os.listdir(WATCH_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic"))
    ])
    return all_images

def is_synced(filepath):
    # Check if the file size remains stable for SYNC_CHECKS consecutive checks
    stable_checks = 0
    last_size = os.path.getsize(filepath)

    while stable_checks < SYNC_CHECKS:
        time.sleep(SYNC_WAIT_TIME)
        current_size = os.path.getsize(filepath)

        if current_size == last_size:
            stable_checks += 1
        else:
            stable_checks = 0
            last_size = current_size

    return True

def wait_for_sync(images):
    # Wait for all images in the batch to finish syncing
    for img in images:
        print(f"⏳ Checking sync status for {img}...")
        is_synced(img)
        print(f"✅ {img} is fully synced.")

def process_batch(front_img, back_img):
    # Pass the image pair to ocr_batch_google.py for processing
    try:
        print(f"📸 Passing batch to OCR script: {front_img}, {back_img}")
        subprocess.run(["python3", OCR_SCRIPT, front_img, back_img], check=True)
    except Exception as e:
        print(f"⚠️ Error passing batch to OCR script: {e}")

def main():
    # Main loop to monitor the watch folder and pass image pairs to ocr_batch_google.py
    print("👀 Watching for new image pairs...")

    while True:
        try:
            new_images = get_new_images()

            # Process in batches of 2
            while len(new_images) >= 2:
                front_img, back_img = new_images[:2]

                # Wait for both images to finish syncing
                wait_for_sync([front_img, back_img])

                # Pass the pair to ocr_batch_google.py
                process_batch(front_img, back_img)

                # Remove processed images
                os.remove(front_img)
                os.remove(back_img)

                # Update the image list
                new_images = get_new_images()

            time.sleep(5)

        except KeyboardInterrupt:
            print("🛑 Watcher stopped manually.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
