from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# Flask uygulaması ve model başlatma
app = Flask(__name__)
model = SentenceTransformer('all-mpnet-base-v2')

# Vektör döndüren endpoint tanımlama
@app.route('/get_vector', methods=['POST'])
def get_vector():
    # JSON isteğinden metni al
    data = request.get_json()
    print(data)
    if 'text' not in data:
        return jsonify({"error": "Request must contain 'text' field"}), 400

    try:
        # Metni vektöre çevirme
        embedding = model.encode(data['text'])

        # Embedding vektörünü listeye çevirip JSON olarak döndürme
        return jsonify({"vector": embedding.tolist()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask uygulamasını çalıştırma
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
