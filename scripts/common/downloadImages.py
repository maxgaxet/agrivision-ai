import os
import requests
from googleapiclient.discovery import build
from requests.exceptions import Timeout

# Replace with your actual API key and custom search engine ID
API_KEY = "AIzaSyAaZ9e7ukrtQzNHAHKg1IJkvsCjAChTPUA"
SEARCH_ENGINE_ID = "45659baa5c1584d03"

def download_images(query, num_images, output_folder, timeout=10):
    # Check existing images
    existing = len([f for f in os.listdir(output_folder) if f.endswith('.jpg')])
    if existing >= num_images:
        print(f"[SKIP] '{query}': Already has {existing} images.")
        return

    print(f"[START] Downloading '{query}' to {output_folder}...")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    service = build("customsearch", "v1", developerKey=API_KEY)
    downloaded = existing
    start_index = 1  # Google Custom Search paginates with start index 1

    while downloaded < num_images:
        res = service.cse().list(
            q=query,
            cx=SEARCH_ENGINE_ID,
            searchType="image",
            num=10,
            start=start_index
        ).execute()

        if "items" not in res:
            print(f"[ERROR] No more results for {query}")
            break

        for item in res["items"]:
            if downloaded >= num_images:
                break

            image_url = item["link"]
            try:
                response = requests.get(image_url, timeout=timeout)
                response.raise_for_status()

                img_path = os.path.join(
                    output_folder,
                    f"{query.replace(' ', '_')}_{downloaded + 1}.jpg"
                )
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                downloaded += 1
                print(f"[{downloaded}/{num_images}] Downloaded: {image_url}")

            except (requests.RequestException, Timeout) as e:
                print(f"[SKIP] Failed to download image: {e}")

        start_index += 10

    print(f"[DONE] {downloaded}/{num_images} images downloaded for '{query}'.")

def download_for_sets(diseases, num_train, num_val, num_test, timeout=10):
    sets = {
        "train": num_train,
        "validation": num_val,
        "test": num_test
    }

    for disease in diseases:
        for set_name, num_images in sets.items():
            folder = os.path.join('data', set_name, 'corn', disease.replace(' ', '_'))
            download_images(disease, num_images, folder, timeout)

# List of diseases
corn_diseases = [
    "corn gray leaf spot",
    "corn common rust",
    "corn northern blight",
    "corn southern rust"
]

# Download image count
num_train_images = 10
num_val_images = 5
num_test_images = 5

# Download!
download_for_sets(corn_diseases, num_train_images, num_val_images, num_test_images)
