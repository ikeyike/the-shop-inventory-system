
import os
import subprocess
from shutil import copy2, move

# Toggle this to True when testing — prevents deleting images
TESTING_MODE = True

def convert_heic_to_jpg_with_sips(heic_path, jpg_path):
    result = subprocess.run(["sips", "-s", "format", "jpeg", heic_path, "--out", jpg_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error converting {heic_path}: {result.stderr}")
    else:
        print(f"Converted HEIC to JPG: {heic_path} -> {jpg_path}")

def rename_and_organize_images(raw_folder, organized_folder, identifier):
    os.makedirs(raw_folder, exist_ok=True)
    target_folder = os.path.join(organized_folder, identifier)
    os.makedirs(target_folder, exist_ok=True)

    image_files = [f for f in os.listdir(raw_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]

    for i, filename in enumerate(sorted(image_files), 1):
        ext = os.path.splitext(filename)[1].lower()
        src = os.path.join(raw_folder, filename)
        new_filename = f"{identifier}_{i}.jpg"  # Always convert to .jpg
        dst = os.path.join(target_folder, new_filename)

        if ext == ".heic":
            convert_heic_to_jpg_with_sips(src, dst)
            if not TESTING_MODE:
                os.remove(src)
                print(f"Deleted original HEIC: {src}")
        else:
            if TESTING_MODE:
                copy2(src, dst)
                print(f"[TEST MODE] Copied: {src} -> {dst}")
            else:
                move(src, dst)
                print(f"Moved and deleted original: {src} -> {dst}")

if __name__ == "__main__":
    RAW_FOLDER = "/Users/naomiabella/My Drive/TheShopRawUploads"
    ORG_FOLDER = "/Users/naomiabella/Desktop/TheShopInventory/OrganizedImages"

    identifier = input("Enter product identifier (e.g., M6916-0918K): ").strip()
    rename_and_organize_images(RAW_FOLDER, ORG_FOLDER, identifier)
#Had to get back to Python3.11 because of .heic issues.