# 🏎️ The Shop Inventory System

## 📚 Table of Contents

- [✅ Features](#-features)
- [📁 Folder Structure](#-folder-structure)
- [🚀 How It Works](#-how-it-works)
- [🔧 Setup Instructions](#-setup-instructions)
- [📌 Changelog](#-changelog)

An automated image-to-inventory pipeline for diecast car collectors (Hot Wheels, Matchbox, etc.). Designed for speed, accuracy, and full automation using iPhone photos, Google Drive, OCR (Vision AI), Python scripts, and a smart Google Sheet.

---

## ✅ Features

- OCR scans for toy numbers (e.g., `M6916-0918K`) from packaging
- Automatically groups front/back images by detected ID
- Renames & organizes photos into `organized_images/[ID]/`
- Converts `.HEIC` → `.JPG` using macOS `sips`
- Skips invalid or corrupted image files
- Auto-upload to Google Drive with public links
- Auto-update your Google Sheet with image URLs
- Optional: auto-fill catalog data from Hot Wheels & Matchbox Wikis
- Fully automated via `watch_folder.py`
- Logs all actions and unmatched photos for review

---

## 📁 Folder Structure

```
the_shop_inventory/
├── the_shop_scripts/
│   ├── ocr_batch_google.py
│   ├── watch_folder.py
│   ├── multi_image_renamer.py         # Fallback option if OCR fails
│   ├── google_sheets_linker.py
│   ├── wiki_catalog_scraper_v2.py
│   ├── processed_images.csv           # 📒 Tracks all handled files
│   ├── unmatched/                     # 📂 Stores images with no toy # detected
│   ├── invalid_images.log             # 🧯 Logs corrupted or unreadable images
├── organized_images/                  # ✅ Final images sorted by product ID
├── ocr_images/                        # Temporary folder for OCR processing
└── Google Drive/My Drive/TheShopRawUploads/
```

---

## 🚀 How It Works

### 🧾 Step-by-Step Flow

1. **Take Two Photos**
   - Photo 1: Front of the car (no toy #)
   - Photo 2: Back of the card (includes toy # like `M6916-0918K`)

2. **Upload via Google Drive**
   - Just drop both photos into the root of `TheShopRawUploads` on your synced Google Drive

3. **`watch_folder.py` detects 2 new images**
   - Moves them into `ocr_images/`
   - Calls `ocr_batch_google.py` to extract toy number via Vision API
   - If found: splits toy number (e.g. keeps `M6916`), renames as `M6916_1.jpg` and `M6916_2.jpg`
   - Stores into: `organized_images/M6916/`

4. **Optionally uploads to Drive**
   - `google_sheets_linker.py` inserts image URLs into Google Sheet row matching Toy #

5. **Optional Catalog Info (auto or manual)**
   - `wiki_catalog_scraper_v2.py` fills in metadata like Collector #, Body Color, Country, etc.
   - Uses fuzzy logic & toy number to match against Wiki pages

6. **Logging**
   - Processed file paths go into `processed_images.csv`
   - Missing toy #? Saved to `/unmatched/`
   - Corrupted file? Logged in `invalid_images.log`

---

## 🔧 Setup Instructions

1. Install Python 3.11 and set `.python-version` to match
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download your Google Vision and Sheets credentials:
   - Save them as `google_vision_key.json` and `credentials.json`
4. Share your Google Drive and Google Sheet with your service account

---

## 📌 Changelog

- ✅ v1.0 – Manual rename & upload scripts
- ✅ v2.0 – Folder automation via `watch_folder.py`
- ✅ v2.3 – Flexible input fallback mode
- ✅ v3.0 – Wiki scraper added with fuzzy matching + CSV log
- ✅ v3.4 – Vision OCR batch processor added with Google Vision AI
- ✅ v3.5 – Toy # detection with smart splitting (`M6916-0918K` → `M6916`)
- ✅ v3.6 – Organized unmatched images & created logging for invalid photos
- ✅ v3.7 – Added fallback `multi_image_renamer.py` for manual batch override
- ✅ v3.8 – Fully dynamic Google Sheets image linking (columns M–Q)