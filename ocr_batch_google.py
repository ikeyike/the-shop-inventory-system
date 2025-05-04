
import os
import re
import shutil
from google.cloud import vision
from PIL import Image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_vision_key.json"
client = vision.ImageAnnotatorClient()

OCR_INPUT_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/ocr_images"
OUTPUT_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/organized_images"
UNMATCHED_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/unmatched_images"
PROCESSED_LOG = "/Users/naomiabella/Desktop/the_shop_inventory/processed_log.txt"

def extract_toy_number(text):
    match = re.search(r"\b([A-Z0-9]{5,})[-]", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def ocr_text_from_image(image_path):
    with open(image_path, "rb") as img_file:
        content = img_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.full_text_annotation.text if response.text_annotations else ""

def log_processed_image(path):
    with open(PROCESSED_LOG, "a") as f:
        f.write(path + "\n")

def move_to_unmatched(images):
    os.makedirs(UNMATCHED_FOLDER, exist_ok=True)
    for img in images:
        dest = os.path.join(UNMATCHED_FOLDER, os.path.basename(img))
        shutil.move(img, dest)
        print(f"❌ Moved unmatched image to: {dest}")
        log_processed_image(img)

def process_batch(images):
    texts = [ocr_text_from_image(img) for img in images]
    toy_numbers = [extract_toy_number(text) for text in texts]

    for i, toy in enumerate(toy_numbers):
        if toy:
            id = toy
            other = images[1 - i]
            labeled_images = [(other, f"{id}_1.jpg"), (images[i], f"{id}_2.jpg")]
            target_folder = os.path.join(OUTPUT_FOLDER, id)
            os.makedirs(target_folder, exist_ok=True)
            for img_src, name in labeled_images:
                dst = os.path.join(target_folder, name)
                shutil.move(img_src, dst)
                log_processed_image(img_src)
                print(f"✅ Moved: {img_src} -> {dst}")
            return
    print("⚠️ No toy number detected in batch.")
    move_to_unmatched(images)

def main():
    files = sorted([os.path.join(OCR_INPUT_FOLDER, f)
                    for f in os.listdir(OCR_INPUT_FOLDER)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))])

    for i in range(0, len(files), 2):
        batch = files[i:i + 2]
        if len(batch) == 2:
            print(f"📸 Processing batch: {batch}")
            process_batch(batch)
        else:
            print(f"⚠️ Incomplete batch: {batch}")
            move_to_unmatched(batch)

if __name__ == "__main__":
    main()
