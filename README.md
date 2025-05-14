
# 🏎️ The Shop Inventory System  

## 📚 Table of Contents  

- [✅ Features](#-features)  
- [📁 Folder Structure](#-folder-structure)  
- [💻 Setting Up the Virtual Environment](#-setting-up-the-virtual-environment)  
- [🚀 How It Works](#-how-it-works)  
- [📌 Changelog](#-changelog)  

An automated image-to-inventory pipeline for diecast car collectors (Hot Wheels, Matchbox, etc.). Designed for speed, accuracy, and full automation using iPhone photos, Google Drive, OCR (Vision AI), Python scripts, and a smart Google Sheet.  

---

## ✅ Features  

- **OCR Scanning:** Extracts Toy # from the back image only, formatted as `M6916-0918K`.  
- **Paired Image Processing:** Processes images in pairs (front and back) and applies the extracted Toy # to both images.  
- **Organized Image Storage:** Images are renamed and moved to `organized_images/[Toy#-Variant]/`.  
- **Image Conversion:** `.HEIC` → `.JPG` using macOS `sips`.  
- **Duplicate Handling:** Skips images already processed and logs them as "Duplicate".  
- **Unmatched Image Management:** Moves unmatched images to `/unmatched/` with logging.  
- **Error Logging:** Tracks errors in `processed_images.csv` with relevant status codes.  
- **Image and Folder Cleanup:** Automatically deletes images and folders in `TheShopRawUploads` after processing.  
- **Google Sheets Integration:** Updates Google Sheets with image paths and variants.  
- **Manual Variant Logging:** Allows manual logging of Toy # and Variant combinations using `multi_image_renamer.py` for unmatched or variant-specific entries.

---

## 📁 Folder Structure  

```
the_shop_inventory/
├── the_shop_scripts/
│   ├── ocr_batch_google.py         # OCR + Google Sheets processing
│   ├── multi_image_renamer.py      # Handles manual processing and unmatched images
│   ├── google_sheets_linker.py     # Updates Google Sheets with image data
│   ├── processed_images.csv        # Log file for processed images
│   ├── unmatched/                  # Unmatched or unreadable images
│   └── invalid_images.log          # Corrupted or unreadable files
├── organized_images/               # Sorted by Toy#-Variant
└── Google Drive/My Drive/TheShopRawUploads/
```

---

## 💻 Setting Up the Virtual Environment  

1. **Navigate to the Project Directory:**
   ```bash
   cd /path/to/the_shop_inventory/the_shop_scripts
   ```

2. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment:**  
   - **macOS/Linux:**  
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**  
     ```bash
     .venv\Scripts\activate
     ```

4. **Install Dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify Installation:**  
   ```bash
   pip list
   ```

6. **Updating `requirements.txt`:**  
   ```bash
   pip freeze > requirements.txt
   ```

7. **Deactivating the Virtual Environment:**  
   ```bash
   deactivate
   ```

---

## 🚀 How It Works  

### 🧾 **Step-by-Step Workflow:**  

1. **Image Capture:**  
   - Capture two photos per car: **front and back**.  
   - Ensure the Toy # is clearly visible in the back image.  

2. **Upload to Google Drive:**  
   - Upload the image pair to `TheShopRawUploads`.  

3. **Processing with `ocr_batch_google.py`:**  
   - Extracts the Toy # from the back image using Google Vision OCR.  
   - Checks for duplicates using `processed_images.csv`.  
   - Renames and organizes images in `organized_images/[Toy#-Variant]/`.  
   - Logs processed images to `processed_images.csv`.  
   - **Deletion:** Images and folders are deleted from `TheShopRawUploads` after processing.  

4. **Manual Variant Logging via `multi_image_renamer.py`:**  
   - `ocr_batch_google.py` cannot distinguish between variants (e.g., color or edition),so use `multi_image_renamer.py`.  
   - This script allows you to manually log the Toy#-Variant by creating a folder in `TheShopRawUploads` with the format `Toy#-Variant` (e.g., `29305-Red`).  
   - Place all related images in the folder and run `multi_image_renamer.py`.  
   - If the variant is not necessary, use only the Toy# as the folder name (e.g., `29305`).  
   - The script applies the specified identifier, logs the files, and moves them to the correct target folder.  
   - **Deletion:** After processing, both images and the source folder are deleted from `TheShopRawUploads`.  

5. **Data Sync with Google Sheets:**  
   - `google_sheets_linker.py` updates Google Sheets with image paths, Toy #, and Variant.  

---

## 📌 Changelog  

- ✅ v1.0 – Manual rename & upload scripts  
- ✅ v2.0 – Folder automation via `watch_folder.py`  
- ✅ v2.3 – Input fallback mode for manual processing  
- ✅ v3.0 – Wiki scraper added with fuzzy matching + CSV log  
- ✅ v3.4 – Vision OCR batch processor added with Google Vision AI  
- ✅ v3.5 – Toy # detection with smart splitting (`M6916-0918K` → `M6916`)  
- ✅ v3.6 – Unmatched images moved to `/unmatched/` with logging  
- ✅ v3.7 – `multi_image_renamer.py` added as a fallback for unmatched processing  
- ✅ v3.8 – Google Sheets linking by Toy # and Variant (M–Q columns)  
- ✅ v3.9 – Simplified workflow; removed intermediate `ocr_images/` folder  
- ✅ v4.0 – Enhanced logging and deletion logic; files only deleted after successful logging  
- ✅ v5.0 – Major workflow update: Removed watch_folder.py, restructured processing flow,     
centralized duplicate handling logic in ocr_batch_google.py and multi_image_renamer.py.  
- ✅ v5.1 – Added virtual environment setup instructions to README.  
- ✅ v5.2 – Enhanced folder cleanup after processing in `multi_image_renamer.py` and `ocr_batch_google.py.`
- ✅ v5.3 – Improved error handling and logging consistency across all scripts.
- ✅ v5.4 – Improved clarity and structure in README for variant logging and processing workflows.



