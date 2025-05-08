import os
import shutil
from PIL import Image
import re

# Configuration
RAW_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
ORG_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/organized_images"
PROCESSED_LOG = "processed_images.csv"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"

def log_processed_image(toy_number, variant):
    with open(PROCESSED_LOG, "a") as log_file:
        log_file.write(f"{toy_number},{variant}\n")

def extract_toy_and_variant(folder_name):
    match = re.match(r"([A-Z0-9]{5,})[-_]?([A-Z0-9]{4,})?", folder_name, re.IGNORECASE)
    if match:
        toy_number = match.group(1).upper()
        variant = match.group(2).upper() if match.group(2) else "NA"
        return toy_number, variant
    return None, None

def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    toy_number, variant = extract_toy_and_variant(folder_name)

    if not toy_number:
        print(f"❌ No valid toy number found in folder: {folder_name}")
        return

    target_folder = os.path.join(ORG_FOLDER, toy_number + "_" + variant)
    os.makedirs(target_folder, exist_ok=True)

    for file_name in os.listdir(folder_path):
        src_path = os.path.join(folder_path, file_name)
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
            dest_file_name = f"{toy_number}_{variant}.jpg"
            dest_path = os.path.join(target_folder, dest_file_name)

            try:
                with Image.open(src_path) as img:
                    img.verify()

                shutil.move(src_path, dest_path)
                print(f"✅ Moved: {src_path} -> {dest_path}")
                log_processed_image(toy_number, variant)

            except Exception as e:
                print(f"⚠️ Failed to process {src_path}: {e}")
                unmatched_dest = os.path.join(UNMATCHED_FOLDER, file_name)
                shutil.move(src_path, unmatched_dest)
                print(f"Moved to unmatched: {unmatched_dest}")

def main():
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    for folder_name in os.listdir(RAW_FOLDER):
        folder_path = os.path.join(RAW_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            process_folder(folder_path)

if __name__ == "__main__":
    main()
