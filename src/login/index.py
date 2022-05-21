from colorama import Cursor
from flask import Flask, jsonify, request, session, jsonify
from werkzeug.security import check_password_hash
import pyodbc

app = Flask (__name__)

driver = 'SQL Server Native Client 11.0'
server = 'localhost'
database = 'LOGIN_TEST'
trusted_connection= 'yes'

try:
    connection = pyodbc.connect ('DRIVER={};SERVER={};DATABASE={};Trusted_Connection={};'.format(
        driver, server, database, trusted_connection
    ))
    cursor = connection.cursor()
except Exception as ex:
    print (ex)


@app.route ("/test")
def test():
    return jsonify(test = 'test')

@app.route ("/")
def home():
    if 'username' in session:
        username = session['username']
        return jsonify (msg = 'You are already logged in', username = username)

    else:
        resp = jsonify (msg = 'Unauthorized')
        resp.status_code = 401
        return resp


@app.route ("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET': 
        return jsonify (msg = 'Hola')
    request_data = request.get_json()
    username = request_data['username']
    password = request_data['password']
    cursor.execute ('SELECT USERNAME, PASSWORD FROM USERS')
    row = cursor.fetchone()
    db_user = row[0]
    db_pass = row[1]
    if username == db_user:
        verify = check_password_hash (db_pass, password)
        if verify: 
            return jsonify (msg = 'Logged')
        else: 
            return jsonify (msg = 'Failed password')
    else: 
        return jsonify (msg = 'Failed username or password')
    

if __name__ == '__main__': 
    app.debug = True
    app.run (host='0.0.0.0', port=3000) 