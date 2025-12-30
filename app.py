from flask import Flask, request, jsonify
from flask_cors import CORS
from chat import get_response
import os

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid request, message required'}), 400

        message = data['message'].strip()
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        response = get_response(message)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in predict: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    