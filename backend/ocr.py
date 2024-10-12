from flask import Flask, request, jsonify
from flask_cors import CORS
from paddleocr import PaddleOCR, draw_ocr
from langdetect import detect
import base64
from io import BytesIO
from PIL import Image
import os
import threading  # Import threading to use lock
import glob

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


# Create a lock to prevent concurrent requests
ocr_lock = threading.Lock()

def clear_temp_files():
    # Delete all temporary image files
    files = glob.glob('*.png')  # Assuming .png images are saved temporarily
    for f in files:
        try:
            os.remove(f)
            print(f"Deleted: {f}")
        except Exception as e:
            print(f"Error deleting file {f}: {e}")

# Call the function to clear old temp files on startup
clear_temp_files()

ocr = PaddleOCR(use_angle_cls=True, lang='japan')
print("Model loaded")

def add_padding(base64_string):
    """Fix incorrect padding in base64 string."""
    return base64_string + '=' * (-len(base64_string) % 4)

@app.route('/api/ocr', methods=['POST'])
def recognize_text():
    global request_count

    # Acquire the lock to prevent concurrent requests
    with ocr_lock:
        # Log incoming request data
        print("Received OCR request")

        # Parse the incoming data
        data = request.get_json()

        if not data or 'image_data' not in data:
            print("No image data provided.")
            return jsonify({"error": "No image data provided"}), 400

        image_data = data.get('image_data')
        print(f"Image data received: {image_data[:100]}")  # Print first 100 chars of base64 string

        # Decode the base64 image
        image_data = image_data.split(",")[1]  # Remove the base64 header
        image_data = add_padding(image_data)  # Fix the base64 padding issue
        image = Image.open(BytesIO(base64.b64decode(image_data)))

        # Save the image to a temporary file
        temp_image_path = "temp_image.png"
        image.save(temp_image_path)

        # Perform OCR
        result = ocr.ocr(temp_image_path, cls=True)
        txts = [elements[1][0] for elements in result[0]]
        print("Raw texts are", txts)
        recognized_text = ''
        for txt in txts:
            try:
                lang = detect(txt)
            except:
                lang = ''
            if lang=='ja':
                recognized_text += txt + '\n'

        # Remove the temporary file after OCR
        os.remove(temp_image_path)

        # Print the interpreted message
        print(f"Text recognized: {recognized_text}")

        # Return the recognized text
        return jsonify({"text": recognized_text})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
