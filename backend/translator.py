from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import EncoderDecoderModel, PreTrainedTokenizerFast, BertJapaneseTokenizer
import threading  # Import threading to use lock

# Initialize the model and tokenizers
encoder_model_name = "cl-tohoku/bert-base-japanese-v2"
decoder_model_name = "skt/kogpt2-base-v2"

src_tokenizer = BertJapaneseTokenizer.from_pretrained(encoder_model_name)
trg_tokenizer = PreTrainedTokenizerFast.from_pretrained(decoder_model_name)

model = EncoderDecoderModel.from_pretrained("sappho192/aihub-ja-ko-translator")
model.eval()  # Set the model to evaluation mode

# Create a lock to prevent concurrent translation requests
translate_lock = threading.Lock()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

@app.route('/api/korean', methods=['POST'])
def translate():
    with translate_lock:  # Acquire the lock to prevent concurrent requests
        print("Received translation request")  # Debugging output

        # Parse the incoming data
        data = request.get_json()
        print(f"Incoming data: {data}")  # Log the incoming request data

        if not data or 'sentence' not in data or not data['sentence'].strip():
            return jsonify({"error": "No text provided"}), 400

        japanese_text = data['sentence']
        print(f"Text received for translation: {japanese_text}")  # Log received text

        # Tokenize and translate the text
        embeddings = src_tokenizer(japanese_text, return_attention_mask=False, return_token_type_ids=False, return_tensors='pt')
        output = model.generate(**embeddings, max_length=500)[0, 1:-1]
        korean_translation = trg_tokenizer.decode(output.cpu())

        # Return the translated text
        return jsonify({"translated_text": korean_translation})

@app.route('/api/korean', methods=['POST', 'OPTIONS'])
def korean_translate():
    if request.method == 'OPTIONS':
        return '', 200  # Respond to preflight requests

    with translate_lock:  # Acquire the lock to prevent concurrent requests
        print("Received Korean translation request")  # Debugging output

        # Parse the incoming data
        data = request.get_json()
        print(f"Incoming data for Korean translation: {data}")  # Log the incoming request data

        if not data or 'sentence' not in data or not data['sentence'].strip():
            return jsonify({"error": "No text provided"}), 400

        japanese_text = data['sentence']
        print(f"Text received for Korean translation: {japanese_text}")  # Log received text

        # Tokenize and translate the text
        embeddings = src_tokenizer(japanese_text, return_attention_mask=False, return_token_type_ids=False, return_tensors='pt')
        output = model.generate(**embeddings, max_length=500)[0, 1:-1]
        korean_translation = trg_tokenizer.decode(output.cpu())
        print(f"Translated Korean text: {korean_translation}")
        # Return the translated text
        return jsonify({"translated_text": korean_translation})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
