from flask import Flask, request, jsonify
from flask_cors import CORS
from paddleocr import PaddleOCR
from PIL import Image
from io import BytesIO
import base64
import os
import threading
from skimage.metrics import structural_similarity as ssim
import numpy as np
import cv2
from langdetect import detect, LangDetectException  # 추가된 모듈

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

ocr_lock = threading.Lock()

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='japan')
print("Model loaded")

# Path to store past input image and recognized text
PAST_IMAGE_PATH = "past_image.png"
PAST_TEXT_PATH = "past_text.txt"


def save_image(image, path):
    """Save image in PNG format to the given path."""
    image.save(path, format="PNG")


def load_past_image(path):
    """Load the past saved image for comparison."""
    if os.path.exists(path):
        return Image.open(path)
    return None


def save_recognized_text(text, path):
    """Save recognized text to a file."""
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)


def load_recognized_text(path):
    """Load recognized text from a file."""
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    return ''


def compare_images(img1, img2):
    """Compare two images and return the similarity score."""
    img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
    img2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)

    # Resize both images to the same size for comparison
    img1 = cv2.resize(img1, (100, 100))
    img2 = cv2.resize(img2, (100, 100))

    score, _ = ssim(img1, img2, full=True)
    return score


def add_padding(base64_string):
    """Fix incorrect padding in base64 string."""
    return base64_string + '=' * (-len(base64_string) % 4)


@app.route('/api/ocr', methods=['POST'])
def recognize_text():
    # Acquire the lock to prevent concurrent requests
    with ocr_lock:
        data = request.get_json()
        if not data or 'image_data' not in data:
            return jsonify({"error": "No image data provided"}), 400

        image_data = data.get('image_data')
        image_data = image_data.split(",")[1]  # Remove the base64 header
        image_data = add_padding(image_data)  # Fix the base64 padding issue
        current_image = Image.open(BytesIO(base64.b64decode(image_data)))

        # Load past image for comparison
        past_image = load_past_image(PAST_IMAGE_PATH)

        if past_image:
            similarity = compare_images(current_image, past_image)
            print(f"Image similarity: {similarity * 100:.2f}%")

            # If similarity is over 95%, do not conduct OCR, return nothing
            if similarity > 0.95:
                print("Skipping OCR due to high similarity with past input.")
                return jsonify({})  # Return empty response to indicate no new data

        # If images are different, save the current image as the new past image
        save_image(current_image, PAST_IMAGE_PATH)

        # Perform OCR
        temp_image_path = "temp_image.png"
        current_image.save(temp_image_path)

        result = ocr.ocr(temp_image_path, cls=True)
        txts = [elements[1][0] for elements in result[0]]

        recognized_text = ''
        for txt in txts:
            try:
                # Detect language
                lang = detect(txt)
                if lang in ['ja', 'zh-cn', 'zh-tw']:  # Filter based on the detected language
                    recognized_text += txt + '<br>'
            except LangDetectException:
                # Handle exception if language detection fails
                print(f"Language detection failed for text: {txt}")
                continue

        # Save recognized text for future requests
        save_recognized_text(recognized_text, PAST_TEXT_PATH)

        # Remove the temporary image file after OCR
        os.remove(temp_image_path)

        print(f"Text recognized: {recognized_text}")
        return jsonify({"text": recognized_text})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
