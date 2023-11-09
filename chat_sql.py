from flask import Flask, render_template, request, redirect, url_for, session, stream_with_context, Response, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import pandas as pd
from passlib.hash import sha256_crypt
import os
from SQL import chat_main
import mysql.connector
import json
import random
import datetime
import sys
import jwt
import stripe
from flask_socketio import SocketIO, emit
import threading
import pytz


cnx = mysql.connector.connect(
    host="localhost", 
    user='root', 
    password='',
    database='workspace'
)

app = Flask(__name__, static_folder= 'Frontend/build/static', template_folder='Frontend/build')
# app = Flask(__name__)
app.secret_key = 'it_will_make_a_random_key.'
CORS(app)
dev_session = []
stripe.api_key = 'sk_test_51N5OhlE9370d8r5CFhJtTVxWjcUpDLWe5ZGsFxX2xxKaS5VVLXvNRXlpxbpwT6h6O198N2APX3HnUATPCPPESGHE00iACqbOFt'
JWT_SECRET_KEY = 'jwt_token_key'

socketio = SocketIO(app, cors_allowed_origins="*")

# handle chat messages
# @socketio.on("chat")
# def handle_chat(email):
#     print(email)
#     emit("chat", email)

def timer_event():
    print("Timer event occured!")

# Serve the React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists("Frontend/build/" + path):
        # Serve the requested file from the React build folder
        return send_from_directory("Frontend/build", path)
    else:
        # Serve the index.html file for all other routes
        return send_from_directory("Frontend/build", "index.html")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route("/bot_get", methods=['POST', 'GET'])
def get_bot_response():
    try:
        userText = request.json['msg']
        print(dev_session)
        query = chat_main.get_query(userText)
        response = Response(chat_main.get_response(userText, query), mimetype='text/event-stream')
        
        response.headers.add('Access-Control-Allow-Origin', '*')
    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route("/random", methods=['POST'])
def randomQuestion():
    random_number = random.randint(0, 99)
    print("random_number", random_number)
    try:
        cnx = mysql.connector.connect(
            user='root', 
            password='',
            database='workspace'
        )
    except mysql.connector.Error as err:
        print('mysql error')

    cursor = cnx.cursor()
    query = f"SELECT random_question FROM random_question WHERE id = {random_number}"
    cursor.execute(query)
    response = cursor.fetchone()

    return jsonify({'msg': response})

@app.route("/reports", methods=['POST'])
def reports():
    try:
        response = Response(chat_main.report(), mimetype='text/event-stream')
        
    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route("/token", methods=['POST'])
def token():
    try:
        userText = request.json['msg']

        print('userText', userText)
        response = Response(chat_main.tokenAnalysis(userText), mimetype='text/event-stream')

    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route("/des", methods=['POST'])
def des():
    try:
        userText = request.json['msg']

        print('userText', userText)
        response = Response(chat_main.tokenDes(userText), mimetype='text/event-stream')

    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route("/marketStatus", methods=['POST'])
def marketStatus():
    try:
        userText = request.json['msg']
        print('userText', userText)

        response = Response(chat_main.marketStatus(), mimetype='text/event-stream')
        print("response", response)
    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route("/trendingToken", methods=['POST'])
def trendingToken():
    try:
        response = Response(chat_main.trendingToken(), mimetype='text/event-stream')
    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route("/coinoftheday", methods=['POST'])
def coinoftheday():
    try:
        response = Response(chat_main.coinoftheday(), mimetype='text/event-stream')
    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route("/AltRank", methods=['POST'])
def AltRank():
    try:
        response = Response(chat_main.AltRank(), mimetype='text/event-stream')
        print("altrank", response)
    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route('/api/user/save_record', methods=['POST'])
def saveRecordIntoDatabase():
    try:
        cnx = mysql.connector.connect(
            user='root', 
            password='',
            database='workspace'
        )
    except mysql.connector.Error as err:
        print('mysql error')
    userHistory = request.json['data']
    token = request.json['token']
    payload = jwt.decode(jwt=token, key=JWT_SECRET_KEY, algorithms=["HS256"])
    if len(userHistory) == 0:
        return jsonify({'msg': 'okay'})
    userHistory_string = json.dumps(userHistory)
    cursor = cnx.cursor()
    query = "SELECT * FROM chat_history WHERE email = %s"
    cursor.execute(query, (payload['email'],))
    if cursor.fetchone() is None:
        query = "INSERT INTO chat_history (email, content) VALUES (%s, %s)"
        cursor = cnx.cursor()
        cursor.execute(query, (payload['email'], userHistory_string,))
        print('none')
    else:
        print('exist')
        cursor = cnx.cursor()
        query = 'UPDATE chat_history SET content = %s WHERE email = %s'
        cursor.execute(query, (userHistory_string, payload['email']))
    cnx.commit()
    cursor.close()
    return jsonify({'msg': 'okay'})

@app.route("/todayNews", methods=['POST'])
def todayNews():
    try:
        response = Response(chat_main.todayNews(), mimetype='text/event-stream')
    except:
        return 'Sorry. please ask me again after one minutes'
    return response

@app.route('/api/user/get_record', methods=['POST'])
def getAllRecords():
    try:
        cnx = mysql.connector.connect(
            user='root', 
            password='',
            database='workspace'
        )
    except mysql.connector.Error as err:
        print('mysql error')
    
    token = request.json['token']
    
    payload = jwt.decode(jwt=token, key=JWT_SECRET_KEY, algorithms=["HS256"])
    cursor = cnx.cursor()
    query = "SELECT * FROM chat_history WHERE email = %s"
    cursor.execute(query, (payload['email'],))
    result = cursor.fetchone()
    if result is None:
        return jsonify({ 'rlt': [] })
    return jsonify({'rlt': json.loads(result[2])})
    
@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')  # Use get() to avoid KeyError if 'email' is not present
    password = request.json.get('password')
    password = sha256_crypt.hash('password')

    if not email or not password:
        return jsonify({"error": "Email or password is required"}), 400
    #check if name and email already exist
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
    user = cursor.fetchone()
    if user:
        return jsonify({"error": "Email already exists"}), 401
    
    query = "INSERT INTO user (email, password) VALUES (%s, %s)"
    cursor.execute(query, (email, password))
    cnx.commit()
    cursor.close()
    return jsonify({"success": "User created successfully"}), 201

# @app.route("/google-login-callback", methods=["POST"])
# @cross_origin()
# def google_login_callback():
#     # Handle the Google login callback
#     # Extract the response data from the request body
#     response_data = request.json
#     print("asd", response_data)

#     # Perform further processing with the response data
#     # (e.g., exchange the authentication token for user information)

#     # Return a response (e.g., user data or success message)
#     return jsonify({"message": "Google login callback processed"})
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        cnx = mysql.connector.connect(
            user='root', 
            password='',
            database='workspace'
        )
    except mysql.connector.Error as err:
        print('mysql error')
    email = request.json['email']  # Use get() to avoid KeyError if 'email' is not present
    password = request.json['password']
    print(email)
    if not email or not password:
        return jsonify({"error": "Email or password is required"}), 400
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
    user = cursor.fetchone()
    isOkay = False
    for sess in dev_session:
        if sess['email'] == email:
            isOkay = True
            break
    if isOkay == False:
        dev_session.append({
            'email': email,
            'info': password
        })
    if user:
        password_sql = user[2]    

        #To compare Passwords            
        if sha256_crypt.verify("password", password_sql):      
            token = jwt.encode(
                payload={'email': email},
                key=JWT_SECRET_KEY
            )
            print("token:", token)
            return jsonify({"success": "Login successful", "userid": user[0], 'token': token}), 200
        else:
            return jsonify({"error": "Incorrect password"}), 402
    else:
        print("Invalid Email Address")
        return jsonify({"error": "Invalid credentials"}), 401

# You can find your endpoint's secret in your webhook settings
endpoint_secret = 'whsec_b3690ad19b8484da6f4a9e8cd8f308c55627d425e1485bd2cb21eba51f3d9873'

@app.route('/webhook', methods=['POST'])
def my_webhook_view():
    try:
        cnx = mysql.connector.connect(
            user='root', 
            password='',
            database='workspace'
        )
    except mysql.connector.Error as err:
        print('mysql error')
    
    cursor = cnx.cursor()
    payload = request.get_data(as_text=True)
    payload_data = json.loads(payload)
    sig_header = request.headers.get('Stripe-Signature')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return abort(400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return abort(400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        if session['payment_status'] == 'paid':
            print("Fulfilling order")
            customer_email = payload_data['data']['object']['customer_details']['email']
            print("email", customer_email)
            print("123123", payload_data)
            
            currentTime = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"
            print("currentTime", currentTime)
            query = "UPDATE user SET date = %s WHERE email = %s"
            cursor.execute(query, (currentTime, customer_email))
            cnx.commit()
            cnx.close()
            token = jwt.encode(
                payload={'email': customer_email},
                key=JWT_SECRET_KEY
            )
            emit('chat', token, namespace="/", broadcast=True)
            print('pay success')
    elif event['type'] == 'checkout.session.async_payment_succeeded':
        print( 'order created' )

    elif event['type'] == 'checkout.session.async_payment_failed':
        print( 'pay failed' )
        
    return '', 200

@app.route('/stripe', methods=['POST'])
def stripeStatus():
    try:
        cnx = mysql.connector.connect(
            user='root', 
            password='',
            database='workspace'
        )
    except mysql.connector.Error as err:
        print('mysql error')
    
    token = request.json['token']
    
    payload = jwt.decode(jwt=token, key=JWT_SECRET_KEY, algorithms=["HS256"])
    cursor = cnx.cursor()
    query = "SELECT date FROM user WHERE email = %s"
    cursor.execute(query, (payload['email'],))
    result = cursor.fetchone()
    print("result", result)
    
    return jsonify(result)

if __name__ == '__main__':
    socketio.run(app, host = '0.0.0.0', port = '80')


