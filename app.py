from flask import Flask, request, jsonify
from agent import run_agent

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({
        "message": "ReAct Agent API 运行中",
        "usage": "POST /ask  body: {\"question\": \"你的问题\"}"
    })

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    
    if not data or "question" not in data:
        return jsonify({"error": "请提供 question 字段"}), 400
    
    question = data["question"]
    
    if not question.strip():
        return jsonify({"error": "问题不能为空"}), 400
    
    result = run_agent(question)
    
    return jsonify({
        "question": question,
        "answer": result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
