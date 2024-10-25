from flask import Flask, request, jsonify
import requests
import pyodbc
import os
import json
import logging

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

# Set up logging for better error tracking

logging.basicConfig(level=logging.INFO)

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
    logging.error(f"Database connection error: {e}")
    exit(1)


@app.route('/tokens', methods=['POST'])
def create_token():
    code = request.json.get('code')
    if code:
        token_response = exchange_code_for_token(code=code)
        if token_response:
            store_token_data(token_response)
            return jsonify({"message": "Token data inserted successfully"}), 201
        else:
            logging.error("Failed to exchange authorization code.")
            return jsonify({"error": "Failed to exchange authorization code"}), 500
    return jsonify({"error": "Authorization code not provided"}), 400


@app.route('/tokens/<string:refresh_token>', methods=['PUT'])
def refresh_token(refresh_token):
    token_response = exchange_code_for_token(refresh_token=refresh_token)
    if token_response:
        store_token_data(token_response)
        return jsonify({"message": "Token data refreshed successfully"}), 200
    else:
        logging.error("Failed to refresh token.")
        return jsonify({"error": "Failed to refresh token"}), 500


# @app.route('/tokens', methods=['GET'])
# def get_token():
#     cursor = conn.cursor()
#     cursor.execute("SELECT TOP 1 * FROM TokenData ORDER BY CreatedAt DESC")
#     row = cursor.fetchone()
#     if row:
#         return jsonify({
#             "user_id": row.UserId,
#             "access_token": row.AccessToken,
#             "refresh_token": row.RefreshToken,
#             "expires_in": row.ExpiresIn,
#             "scope": row.Scope,
#             "token_type": row.TokenType,
#             "created_at": row.CreatedAt
#         }), 200
#     return jsonify({"error": "No token data found"}), 404


def exchange_code_for_token(code=None, refresh_token=None):
    token_url = "https://api.mercadolibre.com/oauth/token"
    payload = {}

    if code:
        payload = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
    elif refresh_token:
        payload = {
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': refresh_token
        }

    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error during token request: {e}")
        return None


def store_token_data(token_data):
    json_string = json.dumps(token_data)
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO TempJsonTable (JsonResponse) VALUES (?)", json_string)
        conn.commit()
        logging.info(f"Token data inserted into TempJsonTable:\n{token_data}")
    except pyodbc.Error as e:
        logging.error(f"Database insert error: {e}")


if __name__ == '__main__':
    app.run(port=int(PORT))
