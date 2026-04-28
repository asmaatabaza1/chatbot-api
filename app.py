from flask import Flask, request, jsonify
from gradio_client import Client, exceptions
import re
import os

app = Flask(__name__)

# تأكد أن الـ Space ID صحيح ومتاح للجميع
HF_SPACE_ID = "SaraSalem/me-app"

@app.route('/chat', methods=['POST'])
def chat():
    # 1. التأكد من استقبال البيانات بصيغة JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    message = data.get('message')
    system_message = data.get('system_message', "You are a friendly Chatbot.")
    max_tokens = data.get('max_tokens', 512)
    temperature = data.get('temperature', 0.7)
    top_p = data.get('top_p', 0.95)

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # 2. تمرير الـ HF_TOKEN للـ Client لضمان عدم حدوث Timeout أو طلب تسجيل دخول
        token = os.environ.get("HF_TOKEN")
        client = Client(HF_SPACE_ID, hf_token=token)
        
        # 3. تعديل طريقة الـ Predict
        # الـ Gradio Client بيحتاج المدخلات بالترتيب وبدون أسماء أحياناً في النسخ الجديدة
        raw_response = client.predict(
            message,
            system_message,
            max_tokens,
            temperature,
            top_p,
            api_name="/chat"
        )

        # 4. معالجة الرد (Gradio قد يعود بـ string أو list)
        if isinstance(raw_response, list):
            raw_response = raw_response[0]
        
        # تنظيف الرد من الـ Tags
        final_response = re.sub(r"\[/?ASS\]", "", str(raw_response)).strip()

        return jsonify({"response": final_response})

    except Exception as e:
        # إرجاع تفاصيل الخطأ الحقيقي للمساعدة في الديباجينج
        return jsonify({
            "error": "Upstream Error from Hugging Face",
            "details": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    return "Chatbot API is running!"

if __name__ == '__main__':
    # Render بيحتاج الـ host يكون 0.0.0.0
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
