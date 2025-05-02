
from google.cloud import vision
from google.oauth2 import service_account
import io
import os
import re

# Setup credentials
CREDENTIAL_PATH = "google_vision_key.json"  # Ensure this is the correct path
credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
client = vision.ImageAnnotatorClient(credentials=credentials)

# Folder to scan
IMAGE_FOLDER = "ocr_images"  # Change this if needed
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".heic")

def extract_toy_number(text):
    return re.findall(r"\b([A-Z]{1}\d{4,5}|\d{5})\b", text)

def process_images():
    for file in os.listdir(IMAGE_FOLDER):
        if file.lower().endswith(SUPPORTED_FORMATS):
            path = os.path.join(IMAGE_FOLDER, file)
            with io.open(path, "rb") as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            response = client.document_text_detection(image=image)

            if response.error.message:
                print(f"⚠️ Error in {file}: {response.error.message}")
                continue

            text = response.full_text_annotation.text
            matches = extract_toy_number(text)
            print(f"{file} ➜ {matches[0] if matches else '❌ No toy number found'}")

if __name__ == "__main__":
    process_images()
