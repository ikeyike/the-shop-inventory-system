import os
import time
import subprocess

# Configuration
WATCH_FOLDER = "/Users/naomiabella/Library/CloudStorage/GoogleDrive-thetrueepg@gmail.com/My Drive/TheShopRawUploads"
SCRIPTS_FOLDER = "/Users/naomiabella/Desktop/the_shop_inventory/the_shop_scripts"
LOG_FILE = "/Users/naomiabella/Desktop/the_shop_inventory/watch_folder.log"
CHECK_INTERVAL = 10  # Check every 10 seconds

def log_message(message):
    """Log a message to the log file."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def run_script(script_name):
    """Run a Python script in the scripts folder."""
    try:
        subprocess.run(["python", os.path.join(SCRIPTS_FOLDER, script_name)], check=True)
        log_message(f"Successfully ran {script_name}")
    except subprocess.CalledProcessError as e:
        log_message(f"Error running {script_name}: {e}")

def main():
    print("Starting watch_folder.py...")
    log_message("Started watch_folder.py")

    while True:
        try:
            # Check if there are any files in the watch folder
            files = [f for f in os.listdir(WATCH_FOLDER) if not f.startswith('.')]
            
            if files:
                log_message(f"Detected files: {files}")

                # Run the ocr_batch_google.py script
                run_script("ocr_batch_google.py")

                # Run the multi_image_renamer.py script
                run_script("multi_image_renamer.py")

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            log_message(f"Error in watch_folder.py: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
