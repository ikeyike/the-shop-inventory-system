
import os
import subprocess
from shutil import copy2, move
from PIL import Image

INVALID_LOG = "invalid_images.log"
PROCESSED_LOG = "processed_images.csv"

def convert_heic_to_jpg_with_sips(heic_path, jpg_path):
    result = subprocess.run(["sips", "-s", "format", "jpeg", heic_path, "--out", jpg_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error converting {heic_path}: {result.stderr}")
    else:
        print(f"Converted HEIC to JPG: {heic_path} -> {jpg_path}")

def is_valid_image(image_path):
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def log_invalid_image(path):
    with open(INVALID_LOG, "a") as f:
        f.write(path + "\n")
    print(f"❌ Invalid image skipped: {path}")

def log_processed_folder(folder_name):
    with open(PROCESSED_LOG, "a") as f:
        f.write(folder_name + "\n")

def rename_and_organize_images(raw_folder, organized_folder):
    folder_name = os.path.basename(raw_folder.rstrip("/"))
    identifier = folder_name
    target_folder = os.path.join(organized_folder, identifier)
    os.makedirs(target_folder, exist_ok=True)

    image_files = [f for f in os.listdir(raw_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))]

    for i, filename in enumerate(sorted(image_files), 1):
        ext = os.path.splitext(filename)[1].lower()
        src = os.path.join(raw_folder, filename)
        new_filename = f"{identifier}_{i}.jpg"
        dst = os.path.join(target_folder, new_filename)

        if ext == ".heic":
            convert_heic_to_jpg_with_sips(src, dst)
            os.remove(src)
            print(f"Deleted original HEIC: {src}")
        else:
            if not is_valid_image(src):
                log_invalid_image(src)
                continue
            move(src, dst)
            print(f"Moved and renamed: {src} -> {dst}")

    log_processed_folder(identifier)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        raw_folder = sys.argv[1]
        organized_folder = sys.argv[2]
    else:
        raw_folder = input("Enter the raw folder path: ").strip()
        organized_folder = input("Enter the organized images path: ").strip()

    rename_and_organize_images(raw_folder, organized_folder)
