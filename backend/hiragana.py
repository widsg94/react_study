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

# Dictionary to convert Katakana to Hiragana
katakana_to_hiragana = {
    'ア': 'あ', 'イ': 'い', 'ウ': 'う', 'エ': 'え', 'オ': 'お',
    'カ': 'か', 'キ': 'き', 'ク': 'く', 'ケ': 'け', 'コ': 'こ',
    'サ': 'さ', 'シ': 'し', 'ス': 'す', 'セ': 'せ', 'ソ': 'そ',
    'タ': 'た', 'チ': 'ち', 'ツ': 'つ', 'テ': 'て', 'ト': 'と',
    'ナ': 'な', 'ニ': 'に', 'ヌ': 'ぬ', 'ネ': 'ね', 'ノ': 'の',
    'ハ': 'は', 'ヒ': 'ひ', 'フ': 'ふ', 'ヘ': 'へ', 'ホ': 'ほ',
    'マ': 'ま', 'ミ': 'み', 'ム': 'む', 'メ': 'め', 'モ': 'も',
    'ヤ': 'や', 'ユ': 'ゆ', 'ヨ': 'よ',
    'ラ': 'ら', 'リ': 'り', 'ル': 'る', 'レ': 'れ', 'ロ': 'ろ',
    'ワ': 'わ', 'ヲ': 'を', 'ン': 'ん',
    'ガ': 'が', 'ギ': 'ぎ', 'グ': 'ぐ', 'ゲ': 'げ', 'ゴ': 'ご',
    'ザ': 'ざ', 'ジ': 'じ', 'ズ': 'ず', 'ゼ': 'ぜ', 'ゾ': 'ぞ',
    'ダ': 'だ', 'ヂ': 'ぢ', 'ヅ': 'づ', 'デ': 'で', 'ド': 'ど',
    'バ': 'ば', 'ビ': 'び', 'ブ': 'ぶ', 'ベ': 'べ', 'ボ': 'ぼ',
    'パ': 'ぱ', 'ピ': 'ぴ', 'プ': 'ぷ', 'ペ': 'ぺ', 'ポ': 'ぽ',
    'キャ': 'きゃ', 'キュ': 'きゅ', 'キョ': 'きょ',
    'シャ': 'しゃ', 'シュ': 'しゅ', 'ショ': 'しょ',
    'チャ': 'ちゃ', 'チュ': 'ちゅ', 'チョ': 'ちょ',
    'ニャ': 'にゃ', 'ニュ': 'にゅ', 'ニョ': 'にょ',
    'ヒャ': 'ひゃ', 'ヒュ': 'ひゅ', 'ヒョ': 'ひょ',
    'ミャ': 'みゃ', 'ミュ': 'みゅ', 'ミョ': 'みょ',
    'リャ': 'りゃ', 'リュ': 'りゅ', 'リョ': 'りょ',
    'ギャ': 'ぎゃ', 'ギュ': 'ぎゅ', 'ギョ': 'ぎょ',
    'ジャ': 'じゃ', 'ジュ': 'じゅ', 'ジョ': 'じょ',
    'ビャ': 'びゃ', 'ビュ': 'びゅ', 'ビョ': 'びょ',
    'ピャ': 'ぴゃ', 'ピュ': 'ぴゅ', 'ピョ': 'ぴょ'
}

# Function to convert Katakana to Hiragana
def katakana_to_hiragana(text):
    hiragana_text = ''
    i = 0
    while i < len(text):
        if i < len(text) - 1 and text[i:i+2] in katakana_to_hiragana:
            # Convert 2-character Katakana combinations (e.g., キャ -> きゃ)
            hiragana_text += katakana_to_hiragana[text[i:i+2]]
            i += 2
        elif text[i] in katakana_to_hiragana:
            # Convert single Katakana characters (e.g., ア -> あ)
            hiragana_text += katakana_to_hiragana[text[i]]
            i += 1
        else:
            # If no conversion is possible, keep the original character
            hiragana_text += text[i]
            i += 1
    return hiragana_text

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
