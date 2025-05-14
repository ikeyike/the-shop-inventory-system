import os
import shutil
import re
from datetime import datetime

RAW_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
ORG_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/organized_images"
LOG_FILE = "/Users/naomiabella/Desktop/the_shop_inventory/processed_images.csv"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
TESTING_MODE = False

def log_processed_image(file_path, identifier, status):
    # Log processed images with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp},{file_path},{identifier},{status}\n")

def is_first_duplicate(identifier):
    # Check if the identifier has been logged as a duplicate before
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
    # Check if the identifier has already been processed
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

def extract_toy_and_variant(folder_name):
    # Extract Toy # and Variant from the folder name
    match = re.match(r"([A-Z0-9]{5})(?:[-_])?(.*)?", folder_name, re.IGNORECASE)
    if match:
        toy_number = match.group(1).upper()
        variant = match.group(2) if match.group(2) else ""
        identifier = f"{toy_number}-{variant}" if variant else toy_number
        print(f"✅ Extracted Identifier: {identifier}")
        return identifier

    print(f"⚠️ No valid identifier found in folder name: {folder_name}")
    return None

def count_existing_files(identifier):
    # Count the number of existing files in the target folder
    target_folder = os.path.join(ORG_FOLDER, identifier)
    existing_files = os.listdir(target_folder) if os.path.exists(target_folder) else []
    count = len([f for f in existing_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))])
    return count

def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    identifier = extract_toy_and_variant(folder_name)

    if not identifier:
        print(f"⚠️ No identifier in folder {folder_name}. Moving files to unmatched.")
        for file_name in os.listdir(folder_path):
            src_path = os.path.join(folder_path, file_name)
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, file_name)
            try:
                if TESTING_MODE:
                    shutil.copy(src_path, unmatched_dest)
                else:
                    shutil.move(src_path, unmatched_dest)
                log_processed_image(src_path, "Unknown", "Unmatched")
            except Exception as e:
                print(f"⚠️ Error moving to unmatched: {e}")
        return

    # Check for duplicates
    if is_duplicate(identifier):
        if is_first_duplicate(identifier):
            print(f"⚠️ First Duplicate Detected for {identifier}")
            log_processed_image("N/A", identifier, "Duplicate")
        else:
            print(f"⚠️ Duplicate (Not Logged) for {identifier}")
        return

    # Create target folder with `-` separator
    target_folder = os.path.join(ORG_FOLDER, identifier)
    os.makedirs(target_folder, exist_ok=True)

    # Start counting from existing files
    file_index = count_existing_files(identifier)

    for file_name in os.listdir(folder_path):
        # Ignore system and hidden files
        if file_name.startswith('.') or file_name.lower() == "icon":
            continue

        src_path = os.path.join(folder_path, file_name)

        # Skip non-image files
        if not file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, file_name)
            try:
                if TESTING_MODE:
                    shutil.copy(src_path, unmatched_dest)
                else:
                    shutil.move(src_path, unmatched_dest)
                log_processed_image(src_path, "Unknown", "Unmatched")
            except Exception as e:
                print(f"⚠️ Error moving to unmatched: {e}")
            continue

        # Increment index for image files
        file_index += 1

        # Construct the new file name using `_` separator
        # Example: 29305_Red_1.jpg or 29305_1.jpg
        identifier_filename = identifier.replace("-", "_")
        new_name = f"{identifier_filename}_{file_index}.jpg"
        dest_path = os.path.join(target_folder, new_name)

        print(f"✅ Moving {src_path} to {dest_path}")

        try:
            if TESTING_MODE:
                shutil.copy(src_path, dest_path)
            else:
                shutil.move(src_path, dest_path)

            log_processed_image(dest_path, identifier, "Processed")

        except Exception as e:
            print(f"⚠️ Error moving {src_path}: {e}")
            log_processed_image(src_path, "Unknown", "Error")

def main():
    print("Starting multi_image_renamer.py...")
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    os.makedirs(ORG_FOLDER, exist_ok=True)

    for folder_name in os.listdir(RAW_FOLDER):
        folder_path = os.path.join(RAW_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            process_folder(folder_path)

if __name__ == "__main__":
    main()
