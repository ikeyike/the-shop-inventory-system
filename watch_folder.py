
import os
import time
import subprocess

RAW_UPLOADS_FOLDER = "/Users/naomiabella/My Drive/TheShopRawUploads"
ARCHIVE_FOLDER = "/Users/naomiabella/My Drive/TheShopRawUploadsProcessed"
CHECK_INTERVAL = 5  # seconds

def get_subfolders(path):
    return [f for f in os.listdir(path)
            if os.path.isdir(os.path.join(path, f)) and not f.startswith('.')]

def run_renamer_with_folder(product_id):
    print(f"📦 Processing folder: {product_id}")
    subprocess.run(["python3", "multi_image_renamer.py"], input=product_id + "\n", text=True)

def run_sheet_updater(product_id):
    print(f"☁️ Uploading and updating sheet for: {product_id}")
    subprocess.run(["python3", "google_sheets_linker.py"], input=product_id + "\n", text=True)

def move_processed_folder(folder_name):
    src = os.path.join(RAW_UPLOADS_FOLDER, folder_name)
    dst = os.path.join(ARCHIVE_FOLDER, folder_name)
    os.makedirs(ARCHIVE_FOLDER, exist_ok=True)
    os.rename(src, dst)
    print(f"📁 Moved processed folder to archive: {dst}")

def main():
    print(f"👀 Watching for new product folders in: {RAW_UPLOADS_FOLDER}")
    seen_folders = set(get_subfolders(RAW_UPLOADS_FOLDER))

    while True:
        time.sleep(CHECK_INTERVAL)
        current_folders = set(get_subfolders(RAW_UPLOADS_FOLDER))
        new_folders = current_folders - seen_folders

        for folder in new_folders:
            product_id = folder.strip()
            run_renamer_with_folder(product_id)
            run_sheet_updater(product_id)
            move_processed_folder(folder)

        seen_folders = set(get_subfolders(RAW_UPLOADS_FOLDER))

if __name__ == "__main__":
    main()
