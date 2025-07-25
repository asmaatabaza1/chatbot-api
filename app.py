from flask import Flask, request, jsonify
from gradio_client import Client
import re

app = Flask(__name__)
HF_SPACE_ID = "asmaaabd0/find-me"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    system_message = data.get('system_message', "You are a friendly Chatbot.")
    max_tokens = data.get('max_tokens', 512)
    temperature = data.get('temperature', 0.7)
    top_p = data.get('top_p', 0.95)

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        client = Client(HF_SPACE_ID)
        raw_response = client.predict(
            message,
            system_message,
            max_tokens,
            temperature,
            top_p,
            api_name="/chat"
        )

        matches = re.findall(r"\[ASS\](.*?)\[/ASS\]", raw_response, re.DOTALL)
        final_response = matches[-1].strip() if matches else raw_response.strip()

        return jsonify({"response": final_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    return "Chatbot API is running!"

if __name__ == '__main__':
    app.run(debug=True)