from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os, base64, requests, uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_ID = "openai/gpt-4o"

def encode_image_to_base64(filepath):
    with open(filepath, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def query_openrouter(image_path, question):
    image_base64 = encode_image_to_base64(image_path)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }
        ],
        "max_tokens": 400,
        "temperature": 0.2
    }
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return {"answer": data["choices"][0]["message"]["content"]}
    else:
        return {"error": f"OpenRouter error: {response.status_code} {response.text}"}

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    image = request.files.get("image")
    question = request.form.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    if image:
        filename = secure_filename(str(uuid.uuid4()) + "_" + image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        session['image_path'] = filepath
        session['chat'] = []
    elif 'image_path' not in session:
        return jsonify({"error": "Please upload an image first."}), 400
    else:
        filepath = session['image_path']

    chat = session.get("chat", [])
    chat.append({"role": "user", "content": question})

    result = query_openrouter(filepath, question)
    answer = result.get("answer", "No answer found.")

    chat.append({"role": "assistant", "content": answer})
    session['chat'] = chat

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)


    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)




