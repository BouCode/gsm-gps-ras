from flask import Flask, jsonify, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, unset_jwt_cookies, get_jwt
from werkzeug.security import check_password_hash
import pyodbc
import requests
from datetime import timedelta, datetime, timezone
import sched, time

app = Flask (__name__)
jwt = JWTManager (app)
app.config["JWT_SECRET_KEY"] = "super-scret"
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

driver = 'SQL Server Native Client 11.0'
server = 'localhost'
database = 'LOGIN_TEST'
trusted_connection= 'yes'

try:
    connection = pyodbc.connect ('DRIVER={};SERVER={};DATABASE={};Trusted_Connection={};'.format(
        driver, server, database, trusted_connection
    ))
    cursor = connection.cursor()
    print('Connect!')

except Exception as exception:
    print (exception)

@app.after_request
def refresh_expiring_jwts(response): 
    try: 
        exp_timestamp = get_jwt()['exp']
        now = datetime.now (timezone.utc)
        target_timestamp = datetime.timestamp (now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp: 
            access_token = create_access_token (identity=get_jwt_identity())
            set_access_cookies (response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


@app.route ("/test")
def test():
    return jsonify(test = 'test')

@app.route ("/")
def home():
    pass

@app.route ("/login", methods=['POST'])
def login():
   
    request_data = request.get_json()
    username = request_data['username']
    password = request_data['password']
    cursor.execute ("SELECT USERNAME, PASSWORD, ID_USER FROM USERS WHERE USERNAME = ?", username)
    row = cursor.fetchone()
    db_user = row[0]
    db_pass = row[1]
    db_id_user = row [2]
    if username == db_user:
        verify = check_password_hash (db_pass, password)
        if verify: 
            msg = jsonify ({'msg' : 'Logged'})
            access_token = create_access_token (identity = db_id_user) 
            print (access_token)
            set_access_cookies (msg,access_token)
            return msg
            
        else: 
            return jsonify (msg = 'Failed password')
    else: 
        return jsonify (msg = 'Failed username or password')
    
@app.route ("/logout", methods = ["POST"])
def logout ():
    response = jsonify (msg = 'Loggout')
    unset_jwt_cookies (response)
    return response


@app.route ("/protected")
@jwt_required()
def protected ():
    return jsonify (foo="bar")

@app.route ("/user")
@jwt_required()
def user():
    current_user_id = get_jwt_identity()
    cursor.execute ("SELECT USERNAME, POSITION FROM USERS WHERE ID_USER = ?", current_user_id)
    row = cursor.fetchone()
    db_user = row[0]
    db_position = row [1]
    response = f'Hola {db_user}. Hoy estás en {db_position}'
    s = sched.scheduler (time.time, time.sleep)

    def do_something(sc):    
        req = requests.get('https://api.wheretheiss.at/v1/satellites/25544').json()
        lat = req['latitude']
        lon = req['longitude']
        timestamp = req['timestamp']
        id_hardware = '2'
        print (f'Latitud: {lat}; Longitud: {lon}; Timestamp: {timestamp}, id_hardware: {id_hardware}')
        cursor.execute ("INSERT INTO GPS_POSITION (LATITUD, LONGITUD, TIMESTAMP, ID_HARDWARE) VALUES (?, ?, ?, ?)", lat, lon, timestamp, id_hardware)
        connection.commit()
        sc.enter (1, 1, do_something, (sc,))
    
    s.enter(1, 1, do_something, (s,))
    s.run()
    return jsonify (msg = response)

if __name__ == '__main__': 
    app.debug = True
    app.run (host='0.0.0.0', port=3000) 