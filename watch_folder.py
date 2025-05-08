
import os
import time
import subprocess
import shutil
from shutil import move

WATCH_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
PROCESSED_LOG = "processed_images.csv"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
OCR_SCRIPT = "ocr_batch_google.py"
SHEETS_SCRIPT = "google_sheets_linker.py"
AUTO_RUN_SHEETS = False

def load_processed_images():
    if not os.path.exists(PROCESSED_LOG):
        return set()
    with open(PROCESSED_LOG, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_processed_image(image_path):
    with open(PROCESSED_LOG, "a") as f:
        f.write(image_path + "\n")

def get_new_images(processed):
    all_images = sorted([
        os.path.join(WATCH_FOLDER, f)
        for f in os.listdir(WATCH_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic"))
    ])
    return [img for img in all_images if img not in processed]

def run_ocr_batch():
    print("📸 Running OCR batch processor...")
    try:
        subprocess.run(["python3", OCR_SCRIPT], check=True)
        print("✅ OCR batch processing complete.")
        return True
    except Exception as e:
        print(f"⚠️ OCR batch script failed: {e}")
        return False

def run_google_sheets_linker():
    print("🔗 Updating Google Sheets...")
    try:
        subprocess.run(["python3", SHEETS_SCRIPT], check=True)
        print("✅ Google Sheets update complete.")
    except Exception as e:
        print(f"⚠️ Sheets update failed: {e}")

def handle_ocr_failure(batch):
    print("⚠️ OCR failed. Moving to unmatched folder.")
    for img in batch:
        shutil.move(img, os.path.join(UNMATCHED_FOLDER, os.path.basename(img)))
        save_processed_image(img)
    print("🟡 Please run multi_image_renamer.py manually on this unmatched batch.")

def main():
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    print("👀 Watching for new image batches...")

    while True:
        try:
            processed = load_processed_images()
            new_images = get_new_images(processed)

            if len(new_images) >= 2:
                batch = new_images[:2]
                print(f"📸 Found batch: {batch}")

                ocr_folder = "/Users/naomiabella/Desktop/the_shop_inventory/ocr_images"
                os.makedirs(ocr_folder, exist_ok=True)
                for img in batch:
                    move(img, os.path.join(ocr_folder, os.path.basename(img)))

                success = run_ocr_batch()
                if not success:
                    handle_ocr_failure(batch)

                if AUTO_RUN_SHEETS and success:
                    run_google_sheets_linker()

            time.sleep(10)

        except KeyboardInterrupt:
            print("\n🛑 Watcher stopped manually.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
