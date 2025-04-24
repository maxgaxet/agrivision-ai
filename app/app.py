import os
import logging
import time
from flask import Flask, request, render_template, jsonify, url_for
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model  # type: ignore
import numpy as np
from PIL import Image
from disease_treatments import disease_treatments  # Import the dictionary

# === Flask Initialization ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, '../models/agrivision_model.h5'))

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Logging Configuration ===
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# === Create Upload Directory ===
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Allowed Extensions ===
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# === Load Model ===
try:
    model = load_model(MODEL_PATH)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    logger.exception("Failed to load the model.")
    raise

# === Class Labels ===
class_labels = [
    "Corn Gray Leaf Spot",
    "Corn Common Rust",
    "Corn Northern Blight",
    "Corn Southern Rust"
]

# === Helper Functions ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def prepare_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        img = img.resize((380, 380))
        img_array = np.array(img) / 255.0
        return np.expand_dims(img_array, axis=0)
    except Exception as e:
        logger.error(f"Error during image preprocessing: {e}")
        raise

def cleanup_upload_folder(threshold_minutes=10):
    """Removes files older than threshold_minutes from the uploads folder"""
    now = time.time()
    threshold = threshold_minutes * 60
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > threshold:
                try:
                    os.remove(file_path)
                    logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")

# === Routes ===

@app.route('/')
def index():
    logger.debug("Rendering index page.")
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    cleanup_upload_folder()  # Clean old files each time predict is called

    try:
        if 'file' not in request.files:
            logger.warning("No file part in request.")
            return jsonify({'error': 'No file part in request'}), 400

        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename received.")
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(local_path)
            logger.info(f"File saved to {local_path}")

            try:
                img_array = prepare_image(local_path)
                prediction = model.predict(img_array)[0]
                class_index = int(np.argmax(prediction))
                confidence = float(prediction[class_index])
                predicted_label = class_labels[class_index] if class_index < len(class_labels) else "Unknown"
                logger.info(f"Predicted: {predicted_label} | Confidence: {confidence:.2f}")
            except Exception as e:
                logger.exception("Error during prediction.")
                return jsonify({'error': 'Error processing image'}), 500

            # Get the disease treatments from the dictionary
            treatments = disease_treatments.get(predicted_label, {})
            cause = treatments.get("cause", "No specific cause available.")
            treatment_methods = treatments.get("treatments", [])

            # Return result
            image_url = url_for('static', filename=f'uploads/{filename}', _external=False)
            return jsonify({
                'prediction': predicted_label,
                'confidence': round(confidence * 100, 2),
                'img_path': image_url,
                'cause': cause,
                'treatments': treatment_methods
            })

        logger.warning("Invalid file type uploaded.")
        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        logger.exception("Unexpected error in /predict route.")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# === Run App ===
if __name__ == '__main__':
    logger.info("Starting AgriVision Flask server...")
    app.run(debug=True)
