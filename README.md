
🏎️ The Shop Inventory System

An automated photo-to-spreadsheet system to catalog diecast cars (Hot Wheels, Matchbox, etc.) using your iPhone, Google Drive, Python, Google Sheets, and wiki-powered AI scraping.

✅ Features

Auto-detect image batches from Google Drive sync

Rename & organize images using product IDs (e.g., M6916-0918K)

Convert .HEIC → .JPG using macOS sips

Upload renamed images to Drive

Auto-update Google Sheets with photo links

Fully automated watch_folder.py that runs with no manual input

Automatically fetches catalog info from Hot Wheels & Matchbox Wikis

Fuzzy Series matching for accuracy

Logs all updates to a CSV file

Works with iPhone and team collaboration

📁 Folder Structure

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

🚀 How It Works

Create a folder named after the product ID (e.g. M6916-0918K)

Place 3–5 photos in it and upload to:
Google Drive > TheShopRawUploads

watch_folder.py detects the folder and runs all automation:

Converts .HEIC to .JPG

Renames files

Moves them to organized_images/[ProductID]/

Uploads to Google Drive

Updates the matching row in your Google Sheet (columns M–Q)

Optionally runs wiki_catalog_scraper_v2.py to fill in missing details from Fandom wikis

Optionally runs ebay_api_scraper.py to pull pricing and log it locally

🔧 Setup Instructions

Install Python 3.11 via pyenv and create .python-version with 3.11.8

Run:

pip install -r requirements.txt

Place credentials.json from Google Cloud in the script folder

Share your Google Sheet and Drive folders with your service account

📌 Changelog

✅ v1.0 – Manual scripts for rename + upload

✅ v1.2 – Added sips HEIC conversion

✅ v2.0 – Folder-based automation via watch_folder.py

✅ v2.1 – iOS Shortcut support (tap to stop)

✅ v2.2 – Removed delay for faster detection

✅ v2.3 – Added input fallback for flexible script use

✅ v3.0 – Integrated Hot Wheels + Matchbox Wiki scraper with fuzzy Series match, Google fallback, and CSV logging

✅ v3.1 – Auto-run wiki scraper from watch_folder.py via toggle

✅ v3.2 – Retired run_toy_lookup.py in favor of full wiki-based automation via wiki_catalog_scraper_v2.py

