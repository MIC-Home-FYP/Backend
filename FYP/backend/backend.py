from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from schedular import ScheduleChecker
from ai_logic import process_query, process_pdf_query
from Agent.chatbot_backend import ChatBot
from DBLogic import DBLogic
import time
import json
from datetime import datetime

"""
To use this code, you need to run the ai_logic,py script then run this script. 
After it's run, you can use the postman app to send Post requests to the server.
"""
app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
dbLogic = DBLogic()


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

@app.route('/signup', methods = ["POST"])
def signup():
    json_content = request.json
    username = json_content.get("username")
    pw_hash = json_content.get("pw_hash")
    dbLogic.insert_signup_info(username, pw_hash)
    return 100

@app.route('/login', methods = ["POST"])
def login():
    json_content = request.json
    username = json_content.get("username")
    pw_hash = json_content.get("pw_hash")
    pw_hash_from_db = dbLogic.get_login_pwhash(username)
    # TODO implement sending back patient id
    # TODO (optional) implement session key
    if pw_hash == pw_hash_from_db:
        return 100
    else:
        return 403
#agent system route
# TODO: Implement patient id and session key
@app.route('/new', methods=["POST"])
def handle_new_chat():
    print("Post /new chat called")
    json_content = request.json
    query = json_content.get("query")
    start=time.process_time()
    print(f"query: {query}")
    # response_answer = ChatBot.respond(query) 
    #to include user_id 
    # user_id = json_content.get("user_id")  # Get user_id from the request
    # if not user_id:
    #     return jsonify({'error': 'user_id is required'}), 400
    user_id = 1
    response_answer = ChatBot.respond(query, user_id)
    print("Response time :",time.process_time()-start)
    return jsonify({'response' : response_answer})


@scheduler.task('interval', id='check_schedules', seconds=60, misfire_grace_time=900)
def check_schedules_job():
    print(f"Scheduler job running at {datetime.now()}")
    with app.app_context():
        print(f"Checking schedules at {datetime.now()}")
        checker = ScheduleChecker()
        checker.check_and_send_notifications()
#for testing       
# def initialize_job():
#     with app.app_context():
#         print("Initializing job...")
#         check_schedules_job()

def start_app():
    # initialize_job() # for testing
    app.run(host= '0.0.0.0', port=8000, debug=True)
    scheduler.start()

if __name__ == "__main__":
    start_app()

