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

- OCR scans for toy numbers (e.g., `M6916-0918K`) from packaging
- Automatically groups front/back images by detected ID
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
│   ├── ocr_batch_google.py
│   ├── watch_folder.py
│   ├── multi_image_renamer.py         # Fallback option if OCR fails
│   ├── google_sheets_linker.py
│   ├── wiki_catalog_scraper_v2.py
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
   - Photo 1: Front of the car (no toy #)
   - Photo 2: Back of the card (includes toy # like `M6916-0918K`)

2. **Upload via Google Drive**
   - Upload both photos to `TheShopRawUploads` in Google Drive.

3. **`watch_folder.py` detects 2 new images**
   - Directly processes images from `TheShopRawUploads`.
   - Logs each image's path, Toy #, Variant, and status (Processed/Unmatched/Error).
   - Deletes images only after logging.

4. **Image Processing via `ocr_batch_google.py`**
   - Extracts Toy # and Variant from the back image.
   - Renames and organizes images in the format `Toy#_1.jpg`, `Toy#_2.jpg`.
   - Moves images to `organized_images/[Toy#-Variant]/`.

5. **Fallback Option: `multi_image_renamer.py`**
   - Handles images that fail OCR or manual batch processing.
   - Logs processed images and handles unmatched files.

6. **Data Upload via `google_sheets_linker.py`**
   - Uploads image URLs to Google Sheets for each Toy # and Variant.
   - Updates specific columns (e.g., M–Q) with image links.

---

## 🔧 Setup Instructions

1. Install Python 3.11 and set `.python-version` to match.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download your Google Vision and Sheets credentials:
   - Save them as `google_vision_key.json` and `credentials.json`.
4. Share your Google Drive and Google Sheet with your service account.

---

## 🛠️ Optional: Auto-Start Configuration

To automatically run `watch_folder.py` on macOS startup, follow these steps:

1. **Create the .plist file:**
   ```bash
   touch ~/Library/LaunchAgents/com.the_shop_inventory.watch_folder.plist
   open -e ~/Library/LaunchAgents/com.the_shop_inventory.watch_folder.plist
   ```

2. **Paste the following into the .plist file:**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.the_shop_inventory.watch_folder</string>
       <key>ProgramArguments</key>
       <array>
           <string>/Users/naomiabella/.pyenv/shims/python3</string>
           <string>/Users/naomiabella/Desktop/the_shop_inventory/the_shop_scripts/watch_folder.py</string>
       </array>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
   </dict>
   </plist>
   ```

3. **Load the Launch Agent:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.the_shop_inventory.watch_folder.plist
   ```

4. **Check the status:**
   ```bash
   launchctl list | grep com.the_shop_inventory.watch_folder
   ```

5. **To stop the Launch Agent:**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.the_shop_inventory.watch_folder.plist
   ```

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
