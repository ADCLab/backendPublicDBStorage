from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import secrets
import time
import re
import os
from pymongo import MongoClient

# Access environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "api_tracking")
API_KEY_EXPIRATION = int(os.getenv("API_KEY_EXPIRATION", 600))
MY_MONGO_HOST = os.getenv("MY_MONGO_HOST")
MY_MONGO_PORT = os.getenv("MY_MONGO_PORT", "27017")
MY_MONGO_USER = os.getenv("MY_MONGO_USER")
MY_MONGO_PASS = os.getenv("MY_MONGO_PASS")
MY_MONGO_DB = os.getenv("MY_MONGO_DB")
MY_MONGO_COLLECTION = os.getenv("MY_MONGO_COLLECTION")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 1))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", 1000))

app = Flask(__name__)
CORS(app, origins=[origin.strip() for origin in CORS_ORIGINS.split(',')])

# MongoDB setup
client = MongoClient(f"mongodb://{MY_MONGO_USER}:{MY_MONGO_PASS}@{MY_MONGO_HOST}:{MY_MONGO_PORT}/")
db = client[MY_MONGO_DB]
collection = db[MY_MONGO_COLLECTION]

# MariaDB Connection Function
def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

# Create API Key
@app.route('/getkey', methods=['GET'])
def generate_api_key():
    api_key = secrets.token_hex(16)
    
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO api_keys (api_key, created_at, expires_at) VALUES (%s, NOW(), NOW() + INTERVAL %s SECOND)", 
            (api_key,API_KEY_EXPIRATION)
        )
        connection.commit()
    
    connection.close()
    return jsonify({"api_key": api_key, "expires_in": API_KEY_EXPIRATION})

# Validate API Key
@app.route('/validatekey/<api_key>', methods=['GET'])
def validatekey(api_key):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT created_at FROM api_keys WHERE api_key = %s", 
            (api_key,)
        )
        result = cursor.fetchone()
    
    connection.close()

    if result:
        expiration_time = result['created_at'].timestamp() + API_KEY_EXPIRATION
        if expiration_time > time.time():
            return jsonify({"valid": True, "expires_in": int(expiration_time - time.time())})
    
    return jsonify({"valid": False, "message": "API key expired or invalid"}), 401

# Insert Data into MongoDB
@app.route('/insert', methods=['POST'])
def store_data():
    api_key = request.headers.get("X-API-KEY")
    content_length = request.content_length

    if not api_key:
        return jsonify({"success": False, "message": "API key is required"}), 400

    # Validate API key
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT created_at FROM api_keys WHERE api_key = %s", 
            (api_key,)
        )
        result = cursor.fetchone()
    connection.close()

    if not result:
        return jsonify({"success": False, "message": "Invalid API key"}), 401

    expiration_time = result['created_at'].timestamp() + API_KEY_EXPIRATION
    if expiration_time <= time.time():
        return jsonify({"success": False, "message": "API key expired"}), 401

    # Validate file size
    if content_length is None:
        return jsonify({"success": False, "message": "No content found in the request"}), 400
    
    if content_length > MAX_FILE_SIZE * 1024 * 1024:
        return jsonify({"success": False, "message": f"File is too large. Maximum size is {MAX_FILE_SIZE} MB."}), 413

    # Check the request payload
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON payload"}), 400

    # Insert sanitized data into MongoDB
    collection.insert_one(data)
    return jsonify({"success": True, "message": "Data stored successfully"})

# Query Values from MongoDB
@app.route('/getvalues', methods=['GET'])
def query_field():
    field = request.args.get('field')

    if not field:
        return jsonify({"success": False, "message": "Field parameter is required"}), 400
    
    try:
        pipeline = [
            {"$match": {field: {"$exists": True}}},
            {"$sample": {"size": SAMPLE_SIZE}},
            {"$project": {field: 1, "_id": 0}}
        ]
        
        results = collection.aggregate(pipeline)
        field_values = [record.get(field) for record in results]

        if not field_values:
            return jsonify({"success": False, "message": f"No records found for the field '{field}'"}), 404
        
        return jsonify({"success": True, "field": field, "values": field_values})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error querying field: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
