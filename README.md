# 🏎️ The Shop Inventory System

## 📚 Table of Contents

- [✅ Features](#-features)
- [📁 Folder Structure](#-folder-structure)
- [🚀 How It Works](#-how-it-works)
- [🔧 Setup Instructions](#-setup-instructions)
- [📌 Changelog](#-changelog)

An automated photo-to-spreadsheet system to catalog diecast cars (Hot Wheels, Matchbox, etc.) using your iPhone, Google Drive, Python, Google Sheets, and wiki-powered AI scraping.

---

## ✅ Features

- Auto-detect image batches from Google Drive sync
- Rename & organize images using product IDs (e.g., M6916-0918K)
- Convert `.HEIC` → `.JPG` using macOS `sips`
- Upload renamed images to Drive
- Auto-update Google Sheets with photo links
- Fully automated `watch_folder.py` that runs with no manual input
- Automatically fetches catalog info from Hot Wheels & Matchbox Wikis
- Fuzzy Series matching for accuracy
- Logs all updates to a CSV file
- Works with iPhone and team collaboration

---

## 📁 Folder Structure

```
the_shop_inventory/
├── the_shop_scripts/
│   ├── ebay_api_scraper.py
│   ├── multi_image_renamer.py
│   ├── google_sheets_linker.py
│   ├── watch_folder.py
│   ├── wiki_catalog_scraper_v2.py
│   ├── requirements.txt
│   └── .python-version
├── organized_images/
├── wiki_update_log.csv
└── Google Drive/My Drive/TheShopRawUploads/
```

---

## 🚀 How It Works

### 🧾 Step-by-Step Workflow

1. **Prepare Your Photos**  
   Create a folder named after the product ID (e.g. `M6916-0918K`). Place 3–5 photos of the diecast car in this folder.

2. **Upload to Google Drive**  
   Upload your folder to `Google Drive > TheShopRawUploads`. Make sure Google Drive sync is running on your Mac.

3. **Automation Begins**  
   `watch_folder.py` will detect the new folder and automatically:
   - Convert `.HEIC` images to `.JPG` using `sips`
   - Rename the images using the product ID
   - Move them to `organized_images/[ProductID]/`
   - Upload the renamed images to Google Drive
   - Update the matching row in your Google Sheet (columns M–Q)

4. **Catalog Info & Pricing (Optional but Recommended)**  
   Depending on your configuration:
   - `wiki_catalog_scraper_v2.py` will run automatically to fill in missing info like Collector #, Series, Base, etc. using Hot Wheels and Matchbox Wiki pages
   - `ebay_api_scraper.py` can run next to search eBay listings and insert the average price into your sheet, while saving a local CSV log

---

## 🔧 Setup Instructions

1. Install Python 3.11 via `pyenv` and create `.python-version` with `3.11.8`
2. Run:
```bash
pip install -r requirements.txt
```
3. Place `credentials.json` from Google Cloud in the script folder
4. Share your Google Sheet and Drive folders with your service account

---

## 📌 Changelog


- ✅ v1.0 – Manual scripts for rename + upload
- ✅ v1.2 – Added `sips` HEIC conversion
- ✅ v2.0 – Folder-based automation via `watch_folder.py`
- ✅ v2.1 – iOS Shortcut support (tap to stop)
- ✅ v2.2 – Removed delay for faster detection
- ✅ v2.3 – Added input fallback for flexible script use
- ✅ v3.0 – Integrated Hot Wheels + Matchbox Wiki scraper with fuzzy Series match, Google fallback, and CSV logging
- ✅ v3.1 – Auto-run wiki scraper from `watch_folder.py` via toggle
- ✅ v3.2 – Retired `run_toy_lookup.py` in favor of full wiki-based automation via `wiki_catalog_scraper_v2.py`
- ✅ v3.3 – Updated README structure, added Table of Contents, removed legacy script references, and documented eBay pricing step