from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from sudachipy import tokenizer
from sudachipy import dictionary

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # Adjust CORS settings if needed

# Initialize SudachiPy tokenizer
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C

# Function to convert Katakana to Hiragana
def katakana_to_hiragana(katakana_text):
    return katakana_text.translate(str.maketrans("アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴァィゥェォャュョッ", 
                                                 "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔぁぃぅぇぉゃゅょっ"))

# Function to convert Kanji to Hiragana, ignoring HTML tags
def kanji_to_hiragana(text):
    # Regular expression to match HTML tags
    tag_regex = re.compile(r'<[^>]+>')
    
    # Split the text by HTML tags, keeping the tags in the result
    parts = tag_regex.split(text)
    tags = tag_regex.findall(text)
    
    # Convert each text part (excluding HTML tags) to Hiragana
    hiragana_parts = []
    for part in parts:
        if part.strip():  # If part is not empty
            tokens = tokenizer_obj.tokenize(part, mode)
            katakana_text = ''.join([m.reading_form() for m in tokens])  # Get Katakana reading
            hiragana_text = katakana_to_hiragana(katakana_text)  # Convert Katakana to Hiragana
            hiragana_parts.append(hiragana_text)
        else:
            hiragana_parts.append(part)

    # Recombine the text with HTML tags interspersed
    result = ''.join([hiragana_parts[i] + (tags[i] if i < len(tags) else '') for i in range(len(hiragana_parts))])
    return result


@app.route('/api/kanji_to_hiragana', methods=['POST'])
def convert_kanji_to_hiragana():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data.get('text')
    print(f"Received text: {text}")    
    # Perform Kanji to Hiragana conversion
    try:
        hiragana_text = kanji_to_hiragana(text)
        print(f"Converted text: {hiragana_text}")
        return jsonify({"hiragana_text": hiragana_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5002, debug=True)
