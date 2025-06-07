# 🏎️ The Shop Inventory System  

## 📚 Table of Contents  

- [✅ Features](#-features)  
- [📁 Folder Structure](#-folder-structure)  
- [💻 Setting Up the Virtual Environment](#-setting-up-the-virtual-environment)  
- [🚀 How It Works](#-how-it-works)  
- [📌 Changelog](#-changelog)  
- [🕰️ Legacy Version](#-legacy-version)

An advanced automation system for cataloging diecast cars (Hot Wheels, Matchbox, etc.) with real-time Google Sheets integration, Google Drive storage, and OCR detection. Built for batch processing, fallback resilience, and a clean upgrade path.

---

## ✅ Features  

- **OCR Toy # Extraction** from back-of-package text (e.g., `M6916-0918K`)  
- **Folder-Based Pair Handling** (e.g., `29289-Black`) to identify Toy # and Variant  
- **Drive Uploads** with public URLs using real file IDs  
- **✔ Sheet Flagging** with a checkmark once upload is complete  
- **Smart Matching Logic:** OCR fallback with image splitting, barcode scanning, and `toy_lookup.json`  
- **Unmatched Routing** for OCR failures (sends to `/unmatched`)  
- **Clean Archiving** of processed folders  
- **Modern Logging System:** `uploaded_to_sheet_log.csv` for traceability  
- **Manual Override Script:** `multi_image_renamer.py` for user-defined control  
- **Variant Booster:** `variant_flagger.py` creates folders and helps sort by variant faster

---

## 📁 Folder Structure  

```
the_shop_inventory/
├── the_shop_scripts/
│   ├── google_sheets_linker.py     # Uploads images and updates Sheet
│   ├── ocr_batch_google.py         # OCR + fallback logic
│   ├── multi_image_renamer.py      # Manual override fallback
│   ├── variant_flagger.py          # Pre-fills variant folders for you
│   ├── requirements.txt            # Python packages
│   ├── toy_lookup.json             # Barcode to Toy # backup
│   ├── unmatched/                  # OCR failures or unrecognized
│   └── uploaded_to_sheet_log.csv   # Master log of uploads
│
├── organized_images/               # Final image storage (Toy#-Variant)
├── archive/                        # Successfully processed folders
└── Google Drive/My Drive/TheShopRawUploads/  # iPhone uploads go here
```

---

## 💻 Setting Up the Virtual Environment  

```bash
cd the_shop_inventory/the_shop_scripts
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

To update dependencies:
```bash
pip freeze > requirements.txt
```

To exit:
```bash
deactivate
```

---

## 🚀 How It Works  

### 🧾 Step-by-Step Workflow  

1. **Upload to `/TheShopRawUploads/`:**  
   - Folder must follow format `29289-Variant` (e.g., `29289-Black`)  
   - Includes 2 images: front and back  

2. **Run `google_sheets_linker.py`:**  
   - Extracts Toy # and Variant from folder name  
   - Uploads both images to Drive  
   - Generates public URLs and adds them to columns N and O  
   - Inserts ✔ into column P once successful  
   - Archives the folder and logs to `uploaded_to_sheet_log.csv`  

3. **If Toy # is unknown:**  
   - Run `ocr_batch_google.py` to try OCR on the back image  
   - If it fails, script tries:
     - Splitting the image
     - Reading the barcode
     - Looking it up in `toy_lookup.json`  
   - Moves unmatchable cases to `/unmatched/`  

4. **Manual Processing:**  
   - Run `multi_image_renamer.py`  
   - This lets you specify the Toy # and Variant manually via folder name  
   - Ideal for unique cases, test runs, or OCR bypass  

5. **Speed Up Sorting:**  
   - Run `variant_flagger.py`  
   - Automatically creates folders like `29289-Red` from Google Sheet data  
   - Helps you prep image batches faster and avoid typing folder names manually  

---

## 📌 Changelog  

- ✅ v1.0 – Base system (manual folder rename + upload)
- ✅ v2.0 – Organized renaming & archiving
- ✅ v3.0 – Google Sheets sync integration
- ✅ v4.0 – OCR automation with fallback image splitting
- ✅ v5.0 – Barcode fallback & lookup JSON support
- ✅ v5.1 – Manual override (`multi_image_renamer.py`)
- ✅ v5.2 – Introduced `uploaded_to_sheet_log.csv` logging
- ✅ v5.3 – ✔ flag added to Sheets for completed rows
- ✅ v5.4 – Archive cleanup after upload success
- ✅ v5.5 – Added `.env` support for sensitive Drive credentials
- ✅ v5.6 – `variant_flagger.py` speeds up sorting + folder creation
- ✅ v5.7 – Final legacy version preserved
- 🚀 v6.0+ – New system version by Roberto with future enhancements

---

## 🕰️ Legacy Version

The original automation flow (v1.0–v5.7) was developed by **Ike**, and included Google Vision OCR, manual renaming tools, and Google Sheets integration.

This legacy version is fully functional and preserved in this repo.

As of v6.0+, the project is being restructured and improved by **Roberto** for enhanced performance and long-term scalability. We will colaborate and use that moving forward. You can access that [here:](https://github.com/rcm-webdev/the-shop) 

---
