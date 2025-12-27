import json
import os
import urllib.request
from datetime import datetime
import zipfile
import shutil

# --- User-friendly drag & drop ---
print("📁 Drag your Snapchat memories_history.json file here and press Enter:")
JSON_FILE = input().strip().strip('"')

print("📂 Drag the folder where you want downloads saved and press Enter:")
OUTPUT_DIR = input().strip().strip('"')

os.makedirs(OUTPUT_DIR, exist_ok=True)
existing_files = set(os.listdir(OUTPUT_DIR))

# --- Load JSON ---
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

media_items = data.get("Saved Media", [])

# --- Helper function to format filename ---
def base_name(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S UTC")
    return dt.strftime("%Y-%m-%d_%H-%M-%S")

# --- Download loop ---
for item in media_items:
    date_str = item.get("Date")
    url = item.get("Media Download Url")
    media_type = item.get("Media Type", "").lower()

    if not date_str or not url:
        continue

    name = base_name(date_str)
    zip_name = f"{name}_memory.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_name)

    # Skip if already processed
    if any(f.startswith(name) for f in existing_files):
        print(f"⏭ Skipping {name} (already exists)")
        continue

    print(f"⬇ Downloading {name}")

    try:
        urllib.request.urlretrieve(url, zip_path)

        # --- Handle ZIP files (captions, videos, images) ---
        if zipfile.is_zipfile(zip_path):
            temp_dir = zip_path + "_unzipped"
            os.makedirs(temp_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(temp_dir)

            os.remove(zip_path)

            for f in os.listdir(temp_dir):
                if f.startswith("._"):
                    continue

                src = os.path.join(temp_dir, f)
                lf = f.lower()

                if lf.endswith(".png"):
                    out = f"{name}_caption.png"
                elif lf.endswith(".jpg"):
                    out = f"{name}_image.jpg"
                elif lf.endswith(".mp4"):
                    out = f"{name}_video.mp4"
                else:
                    continue

                if out in existing_files:
                    continue

                shutil.move(src, os.path.join(OUTPUT_DIR, out))
                existing_files.add(out)

            shutil.rmtree(temp_dir)

        # --- Non-zip media ---
        else:
            ext = ".mp4" if media_type == "video" else ".jpg"
            out = f"{name}{ext}"
            shutil.move(zip_path, os.path.join(OUTPUT_DIR, out))
            existing_files.add(out)

    except Exception as e:
        print(f"❌ Failed: {e}")

print("✅ Snapchat memories download complete")
