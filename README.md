# 🏎️ The Shop Inventory System

## 📚 Table of Contents

- [✅ Features](#-features)
- [📁 Folder Structure](#-folder-structure)
- [🚀 How It Works](#-how-it-works)
- [🔧 Setup Instructions](#-setup-instructions)
- [🛠️ Optional: Auto-Start Configuration](#-optional-auto-start-configuration)
- [📌 Changelog](#-changelog)

An automated image-to-inventory pipeline for diecast car collectors (Hot Wheels, Matchbox, etc.). Designed for speed, accuracy, and full automation using iPhone photos, Google Drive, OCR (Vision AI), Python scripts, and a smart Google Sheet.

---

## ✅ Features

- OCR scans for toy numbers (e.g., `M6916-0918K`) from the **back image only**
- Processes images in pairs (front and back) - Toy # is only extracted from the back image and applied to both
- Renames & organizes photos into `organized_images/[Toy#-Variant]/`
- Converts `.HEIC` → `.JPG` using macOS `sips`
- Skips invalid or corrupted image files
- Auto-upload to Google Drive with public links
- Auto-update your Google Sheet with image URLs
- Fully automated via `watch_folder.py`
- Logs all actions, including unmatched and invalid photos, for review
- Deletes images only after successful logging to `processed_images.csv`

---

## 📁 Folder Structure

```
the_shop_inventory/
├── the_shop_scripts/
│   ├── batch_processing.py             # New processing logic for paired images
│   ├── ocr_batch_google.py
│   ├── watch_folder.py
│   ├── multi_image_renamer.py         # Fallback option if OCR fails
│   ├── google_sheets_linker.py
│   ├── processed_images.csv           # 📒 Tracks all handled files
│   ├── unmatched/                     # 📂 Stores images with no toy # detected
│   ├── invalid_images.log             # 🧯 Logs corrupted or unreadable images
├── organized_images/                  # ✅ Final images sorted by Toy#-Variant
└── Google Drive/My Drive/TheShopRawUploads/
```

---

## 🚀 How It Works

### 🧾 Step-by-Step Flow

1. **Take Two Photos**
   - Photo 1: Front of the car (no toy # expected)
   - Photo 2: Back of the card (includes toy # like `M6916-0918K`)

2. **Upload via Google Drive**
   - Upload both photos to `TheShopRawUploads` in Google Drive.

3. **Batch Processing Logic in `watch_folder.py`:**
   - Processes images **in pairs (front and back)**.
   - If only **one image is present**, it waits for the second image before proceeding.
   - **Order of Images:**  
     - The first image in the batch is considered the **front**, and the second is considered the **back**.
     - The Toy # is **only extracted from the back image** and applied to both images in the pair.
   - Logs each image's path, Toy #, Variant, and status (Processed/Unmatched/Error).
   - Deletes images only after logging.

4. **Image Processing via `ocr_batch_google.py`**
   - Extracts Toy # and Variant from the back image.
   - Renames and organizes images in the format `Toy#_1.jpg` (front) and `Toy#_2.jpg` (back).
   - Moves images to `organized_images/[Toy#-Variant]/`.

5. **Unmatched Handling:**
   - If the Toy # is not detected in the back image, both images in the pair are moved to the `unmatched` folder.
   - The pair is logged as "Unmatched" in `processed_images.csv`.

6. **Fallback Option: `multi_image_renamer.py`**
   - Handles images that fail OCR or require manual processing.

7. **Data Upload via `google_sheets_linker.py`**
   - Updates Google Sheets with image paths and variants.

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
- ✅ v4.1 – Optional auto-start configuration for `watch_folder.py` using Launch Agents
- ✅ v4.2 – Updated batch processing to handle paired images (front and back) and apply Toy # from the back image to both.
- ✅ v4.3 – Enhanced batch processing logic to wait for the second image and enforce front/back order processing.
