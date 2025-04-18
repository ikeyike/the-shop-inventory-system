
import os
import time
import subprocess

AUTO_RUN_WIKI = True  # 🔁 Toggle to automatically run the wiki scraper

# Simulated placeholder for your watch_folder logic
def run_image_processing():
    print("📸 Processing images...")
    time.sleep(2)
    print("✅ Image processing complete.")

# Main automation
def main():
    run_image_processing()

    if AUTO_RUN_WIKI:
        print("📚 Auto-running wiki_catalog_scraper_v2.py for catalog info...")
        try:
            subprocess.run(["python3", "wiki_catalog_scraper_v2.py"], check=True)
            print("✅ Wiki scraper completed.")
        except Exception as e:
            print(f"⚠️ Failed to run wiki scraper: {e}")

if __name__ == "__main__":
    main()
