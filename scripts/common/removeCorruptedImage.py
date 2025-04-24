from PIL import Image, UnidentifiedImageError
import os

def remove_corrupt_images(directory):
    removed = 0
    for root, dirs, files in os.walk(directory):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with Image.open(fpath) as img:
                    img.verify()
            except (UnidentifiedImageError, IOError, SyntaxError):
                print(f"❌ Removing corrupt image: {fpath}")
                os.remove(fpath)
                removed += 1
    print(f"\n✅ Done. Removed {removed} corrupt images from {directory}.\n")

# Paths to check
remove_corrupt_images("data/train")
remove_corrupt_images("data/validation")
remove_corrupt_images("data/test")
