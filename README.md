
# 🏎️ The Shop Inventory System

An automated photo-to-spreadsheet system to catalog diecast cars (Hot Wheels, Matchbox, etc.) using your iPhone, Google Drive, Python, and Google Sheets.

---

## ✅ Features

- Auto-detect image batches from Google Drive sync
- Rename & organize images using product IDs (e.g., M6916-0918K)
- Convert `.HEIC` → `.JPG` using macOS `sips`
- Upload renamed images to Drive
- Auto-update Google Sheets with photo links
- Fully automated `watch_folder.py` that requires no manual input
- Works with iPhone and team collaboration
- Includes iOS Shortcut option for easy on-the-go uploads

---

## 📁 Folder Structure

```
the_shop_inventory/
├── the_shop_scripts/
│   ├── multi_image_renamer.py
│   ├── google_sheets_linker.py
│   ├── watch_folder.py
│   └── requirements.txt
├── organized_images/
└── Google Drive/My Drive/TheShopRawUploads/
```

---

## 🚀 How It Works

1. Create a folder named after the product ID (e.g. `M6916-0918K`)
2. Place 3–5 photos in it and upload to:
   `Google Drive > TheShopRawUploads`
3. `watch_folder.py` detects the folder, runs all automation:
   - Converts `.HEIC` to `.JPG`
   - Renames files
   - Moves them to `organized_images/[ProductID]/`
   - Uploads to Google Drive
   - Updates the matching row in your Google Sheet (columns M–Q)

---

## 🔧 Setup Instructions

1. Install Python 3.11 via `pyenv`
2. Run:
```bash
pip install -r requirements.txt
```
3. Place `credentials.json` from Google Cloud in the script folder
4. Share your Google Sheet and Drive folders with your service account

---

## 📲 iOS Shortcut

Use the "Diecast Photo Uploader" Shortcut:
- Prompts for product ID
- Opens camera for repeated photos
- Saves directly to `TheShopRawUploads/[ProductID]/`
- Syncs and triggers automation on your Mac

See `Shortcut_Setup_Guide.png` for visual instructions.

---

## 📌 Changelog

- ✅ v1.0 – Manual scripts for rename + upload
- ✅ v1.2 – Added `sips` HEIC conversion
- ✅ v2.0 – Folder-based automation via `watch_folder.py`
- ✅ v2.1 – iOS Shortcut support (tap to stop)
- ✅ v2.2 – Removed delay for faster detection
- ✅ v2.3 – Added input fallback for flexible script use
