import os
from PIL import Image, UnidentifiedImageError

# Resize settings
TARGET_SIZE = (380, 380)
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')

# Folders to process
DATA_DIRS = ['data/train', 'data/validation', 'data/test']

def resize_images_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(IMAGE_EXTENSIONS):
                file_path = os.path.join(root, filename)
                try:
                    img = Image.open(file_path)
                    img = img.convert("RGB")
                    img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                    img.save(file_path)
                    print(f"✅ Resized: {file_path}")
                except UnidentifiedImageError:
                    print(f"❌ Unreadable image: {file_path}")
                except Exception as e:
                    print(f"❌ Error processing {file_path}: {e}")

def main():
    for dir_path in DATA_DIRS:
        print(f"🔄 Processing {dir_path}...")
        resize_images_in_folder(dir_path)
    print("🎉 All valid images resized.")

if __name__ == "__main__":
    main()
