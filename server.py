from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import pyodbc
import os
import json

# Required to read the env vars
load_dotenv()

# Credentials and configurations
CLIENT_ID = os.getenv('YOUR_CLIENT_ID')
CLIENT_SECRET = os.getenv('YOUR_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
PORT = os.getenv('PORT')
SERVER = os.getenv('SQL_SERVER')
DB_NAME = os.getenv('SQL_DATABASE')
DB_USER = os.getenv('SQL_USER')
DB_PASSWORD = os.getenv('SQL_PASSWORD')

app = Flask(__name__)

# Database connection details using environment variables
try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=' + SERVER + ';'
        'DATABASE=' + DB_NAME + ';'
        'UID=' + DB_USER + ';'
        'PWD=' + DB_PASSWORD
    )
except pyodbc.Error as e:
    print(f"Database connection error: {e}")
    exit(1)


@app.route('/', methods=['GET'])
def home():
    return (f"Welcome to the callback server"), 200


@app.route('/callback', methods=['GET'])
def callback():
    # Get the 'code' parameter from the query string
    code = request.args.get('code')
    
    if code:
        # Exchange the code for an access token
        token_response = exchange_code_for_token(code)
        
        # If the token exchange was successful, return the response
        if token_response:
            store_token_data(token_response)
            return jsonify({"": f"Token data inserted successfully:\n{token_response}"}), 200
        else:
            return jsonify({"error": "Error exchanging code for token"}), 500
    else:
        return jsonify({"error": "Authorization code not found"}), 400


def exchange_code_for_token(code):
    # Define the token endpoint
    token_url = "https://api.mercadolibre.com/oauth/token"
    
    # Prepare the data payload
    payload = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    # Make the POST request to exchange the code for an access token
    response = requests.post(token_url, data=payload)
    
    # Check if the request was successful and return the JSON response
    if response.status_code == 200:
        return response.json()  # Return JSON response with access token
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    

def store_token_data(token_data):
    json_string = json.dumps(token_data)
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO TempJsonTable (JsonResponse) VALUES (?)", json_string)
        conn.commit()
        print(f"Token data inserted into TempJsonTable:\n{token_data}")
    except pyodbc.Error as e:
        print(f"Database insert error: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
