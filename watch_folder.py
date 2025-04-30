
import os
import time
import subprocess

WATCH_FOLDER = "/Users/naomiabella/My Drive/TheShopRawUploads"
PROCESSED_LOG = "processed_folders.log"

def load_processed_folders():
    if not os.path.exists(PROCESSED_LOG):
        return set()
    with open(PROCESSED_LOG, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_processed_folder(folder_name):
    with open(PROCESSED_LOG, "a") as f:
        f.write(folder_name + "\n")

def run_image_renamer(folder_path, folder_name):
    print(f"📸 Processing: {folder_name}")
    try:
        subprocess.run(["python3", "multi_image_renamer.py", folder_path, folder_name], check=True)
        print("✅ Image renaming complete.")
    except Exception as e:
        print(f"⚠️ Error in image renaming: {e}")

def main():
    processed_folders = load_processed_folders()
    print("👀 Watching for new folders...")

    while True:
        try:
            current_folders = {f for f in os.listdir(WATCH_FOLDER)
                               if os.path.isdir(os.path.join(WATCH_FOLDER, f))}
            new_folders = current_folders - processed_folders

            for folder_name in new_folders:
                folder_path = os.path.join(WATCH_FOLDER, folder_name)
                run_image_renamer(folder_path, folder_name)
                save_processed_folder(folder_name)

            time.sleep(10)  # Poll every 10 seconds
        except KeyboardInterrupt:
            print("\n🛑 Watcher stopped manually.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
