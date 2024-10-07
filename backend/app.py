from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModel, AutoTokenizer
import base64
from io import BytesIO
from PIL import Image
import torch
import os

# Initialize the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True, 
                                  low_cpu_mem_usage=True, device_map='cuda', 
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
print("Model is loaded")

app = Flask(__name__)

CORS(app, origins=["http://localhost:3000"])

def add_padding(base64_string):
    """Fix incorrect padding in base64 string."""
    return base64_string + '=' * (-len(base64_string) % 4)

@app.route('/api/ocr', methods=['POST'])
def ocr():
    try:
        # Log incoming request data
        print("Received OCR request")

        # Parse the incoming data
        data = request.get_json()

        if not data or 'image_data' not in data:
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
        recognized_text = model.chat(tokenizer, temp_image_path, ocr_type='ocr')

        # Remove the temporary file after OCR
        os.remove(temp_image_path)

        # Return the recognized text
        return jsonify({"text": recognized_text})

    except Exception as e:
        print(f"Error during OCR processing: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
