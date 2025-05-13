import os
import shutil
import re

RAW_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
ORG_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/organized_images"
PROCESSED_LOG = "processed_images.csv"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched"
TESTING_MODE = True

def log_processed_image(file_path, toy_number, variant, status):
    with open(PROCESSED_LOG, "a") as log_file:
        log_file.write(f"{file_path},{toy_number},{variant},{status}\n")

def is_duplicate(file_path):
    with open(PROCESSED_LOG, "r") as log_file:
        return any(file_path in line for line in log_file)

def extract_toy_and_variant(folder_name):
    match = re.match(r"([A-Z0-9]{5,})[-_]?([A-Z0-9]{4,})?", folder_name, re.IGNORECASE)
    if match:
        return match.group(1).upper(), (match.group(2).upper() if match.group(2) else "")
    return None, None

def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    toy_number, variant = extract_toy_and_variant(folder_name)

    if not toy_number:
        for file_name in os.listdir(folder_path):
            src_path = os.path.join(folder_path, file_name)
            unmatched_dest = os.path.join(UNMATCHED_FOLDER, file_name)
            if TESTING_MODE:
                shutil.copy(src_path, unmatched_dest)
            else:
                shutil.move(src_path, unmatched_dest)
            log_processed_image(src_path, "Unknown", "Unknown", "Unmatched")
        return

    target_folder = os.path.join(ORG_FOLDER, f"{toy_number}-{variant}" if variant else toy_number)
    os.makedirs(target_folder, exist_ok=True)

    for file_name in os.listdir(folder_path):
        src_path = os.path.join(folder_path, file_name)

        if is_duplicate(src_path):
            log_processed_image(src_path, "Unknown", "Unknown", "Duplicate")
            continue

        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
            try:
                new_name = f"{toy_number}_{variant}_{file_name}" if variant else f"{toy_number}_{file_name}"
                dest_path = os.path.join(target_folder, new_name)

                if TESTING_MODE:
                    shutil.copy(src_path, dest_path)
                else:
                    shutil.move(src_path, dest_path)

                log_processed_image(dest_path, toy_number, variant if variant else "NA", "Processed")
            except Exception as e:
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
