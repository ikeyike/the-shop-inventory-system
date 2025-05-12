import os
import shutil
from PIL import Image
import re

# Configuration
RAW_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
ORG_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/organized_images"
PROCESSED_LOG = "processed_images.csv"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
TESTING_MODE = True  # Toggle to prevent deletion of source images during testing

def log_processed_image(file_path, toy_number, variant, status):
    """ Log each processed image with file path, toy number, variant, and status. """
    with open(PROCESSED_LOG, "a") as log_file:
        log_file.write(f"{file_path},{toy_number},{variant},{status}\n")

def extract_toy_and_variant(folder_name):
    """ Extract Toy # and Variant from folder name. """
    match = re.match(r"([A-Z0-9]{5,})[-_]?([A-Z0-9]{4,})?", folder_name, re.IGNORECASE)
    if match:
        toy_number = match.group(1).upper()
        variant = match.group(2).upper() if match.group(2) else ""
        return toy_number, variant
    return None, None

def process_folder(folder_path):
    """ Process each folder and move or copy images to the organized folder structure. """
    folder_name = os.path.basename(folder_path)
    toy_number, variant = extract_toy_and_variant(folder_name)

    if not toy_number:
        print(f"❌ No valid toy number found in folder: {folder_name}")
        for file_name in os.listdir(folder_path):
            src_path = os.path.join(folder_path, file_name)
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, file_name)

            if TESTING_MODE:
                shutil.copy(src_path, unmatched_dest)
            else:
                shutil.move(src_path, unmatched_dest)

            log_processed_image(src_path, "Unknown", "Unknown", "Unmatched")
        return

    # Create target folder
    target_folder_name = f"{toy_number}"
    if variant:
        target_folder_name += f"_{variant}"
        
    target_folder = os.path.join(ORG_FOLDER, target_folder_name)
    os.makedirs(target_folder, exist_ok=True)

    for file_name in os.listdir(folder_path):
        src_path = os.path.join(folder_path, file_name)

        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
            try:
                with Image.open(src_path) as img:
                    img.verify()

                # Rename and move/copy the file
                if variant:
                    new_name = f"{toy_number}_{variant}_{file_name}"
                else:
                    new_name = f"{toy_number}_{file_name}"

                dest_path = os.path.join(target_folder, new_name)

                # Move or copy based on TESTING_MODE
                if TESTING_MODE:
                    shutil.copy(src_path, dest_path)
                else:
                    shutil.move(src_path, dest_path)

                log_processed_image(dest_path, toy_number, variant if variant else "NA", "Processed")
                print(f"✅ Processed: {src_path} -> {dest_path}")

            except Exception as e:
                print(f"⚠️ Error processing {src_path}: {e}")
                unmatched_dest = os.path.join(UNMATCHED_FOLDER, file_name)

                if TESTING_MODE:
                    shutil.copy(src_path, unmatched_dest)
                else:
                    shutil.move(src_path, unmatched_dest)

                log_processed_image(src_path, "Unknown", "Unknown", "Error")
        else:
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, file_name)

            if TESTING_MODE:
                shutil.copy(src_path, unmatched_dest)
            else:
                shutil.move(src_path, unmatched_dest)

            log_processed_image(src_path, "Unknown", "Unknown", "Unmatched")

def main():
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    os.makedirs(ORG_FOLDER, exist_ok=True)

    for folder_name in os.listdir(RAW_FOLDER):
        folder_path = os.path.join(RAW_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            process_folder(folder_path)

if __name__ == "__main__":
    main()
