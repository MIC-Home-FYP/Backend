from flask import Flask, request, jsonify
from dotenv import load_dotenv
from ai_logic import process_query, process_pdf_query

#load_dotenv()
app = Flask(__name__)


@app.route('/ai', methods=["POST"])
def aiPost():
    print("post /ai called")
    input_json = request.json
    query = input_json.get("query")
    print(f"query: {query}")
    response_content = process_query(query)
    response_answer = {"Sample response": response_content}
    return jsonify(response_answer)

@app.route('/aipdf', methods=["POST"])
def askPDFPost():
    print("Post /ask_pdf called")
    json_content = request.json
    query = json_content.get("query")
    print(f"query: {query}")
    response_answer = process_pdf_query(query)
    return jsonify(response_answer)

def start_app():
    app.run(port=8000, debug=True)

if __name__ == "__main__":
    start_app()

