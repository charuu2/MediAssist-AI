from flask import Flask, render_template, request, jsonify
from backend import ask_question

app = Flask(__name__)  # default: templates=templates, static=static

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message")
    answer, sources = ask_question(user_message)
    return jsonify({"answer": answer, "sources": sources})
    
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

