from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import EncoderDecoderModel, PreTrainedTokenizerFast, BertJapaneseTokenizer
import torch

# Initialize the model and tokenizers
encoder_model_name = "cl-tohoku/bert-base-japanese-v2"
decoder_model_name = "skt/kogpt2-base-v2"

src_tokenizer = BertJapaneseTokenizer.from_pretrained(encoder_model_name)
trg_tokenizer = PreTrainedTokenizerFast.from_pretrained(decoder_model_name)

model = EncoderDecoderModel.from_pretrained("sappho192/aihub-ja-ko-translator")
model.eval()  # Set the model to evaluation mode

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        print("Received translation request")  # Debugging output

        # Parse the incoming data
        data = request.get_json()
        print(f"Incoming data: {data}")  # Log the incoming request data

        if not data or 'sentence' not in data:
            return jsonify({"error": "No text provided"}), 400

        japanese_text = data['sentence']
        print(f"Text received for translation: {japanese_text}")  # Log received text

        # Tokenize and translate the text
        embeddings = src_tokenizer(japanese_text, return_attention_mask=False, return_token_type_ids=False, return_tensors='pt')
        output = model.generate(**embeddings, max_length=500)[0, 1:-1]
        korean_translation = trg_tokenizer.decode(output.cpu())

        # Return the translated text
        return jsonify({"translated_text": korean_translation})

    except Exception as e:
        print(f"Error during translation processing: {str(e)}")  # Log error
        return jsonify({"error": str(e)}), 500

@app.route('/api/korean', methods=['POST', 'OPTIONS'])
def korean_translate():
    if request.method == 'OPTIONS':
        return '', 200  # Respond to preflight requests

    try:
        print("Received Korean translation request")  # Debugging output

        # Parse the incoming data
        data = request.get_json()
        print(f"Incoming data for Korean translation: {data}")  # Log the incoming request data

        if not data or 'sentence' not in data:
            return jsonify({"error": "No text provided"}), 400

        japanese_text = data['sentence']
        print(f"Text received for Korean translation: {japanese_text}")  # Log received text

        # Tokenize and translate the text
        embeddings = src_tokenizer(japanese_text, return_attention_mask=False, return_token_type_ids=False, return_tensors='pt')
        output = model.generate(**embeddings, max_length=500)[0, 1:-1]
        korean_translation = trg_tokenizer.decode(output.cpu())

        # Return the translated text
        return jsonify({"translated_text": korean_translation})

    except Exception as e:
        print(f"Error during Korean translation processing: {str(e)}")  # Log error
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
