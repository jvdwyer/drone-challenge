from flask import Flask, request, jsonify
import jwt
import datetime
import json
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'

CONFIG_FILE_PATH = 'config/application_settings.json'

def read_user_credentials():
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            user_data = json.load(config_file)
            return user_data
    return None

def write_user_credentials(username, password):
    user_data = {'username': username, 'password': password}

    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(user_data, config_file)
    
def validate_user_credentials(auth):
    user_credentials = read_user_credentials()

    if auth and auth.username == user_credentials['username'] and auth.password == user_credentials['password']:
        return True
    else:
        return False

@app.route('/get_token', methods=['GET'])
def get_token():
    auth = request.authorization

    if validate_user_credentials(auth):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        
        token = jwt.encode({'username': auth.username, 'exp': expiration_time}, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token, 'expires_in': 3600})
    else:
        return jsonify({'error': 'Unauthorized'}), 401

@app.route('/validate_token', methods=['POST'])
def validate_token():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'error': 'Token not present'}), 401
    
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

        if datetime.datetime.utcnow() < datetime.datetime.utcfromtimestamp(decoded_token['exp']):
            return jsonify({'message': 'Token is valid'}), 200
        else:
            return jsonify({'error': 'Token has expired'}), 401
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    
@app.route('/change_credentials', methods=['POST'])
def change_credentials():
    auth = request.authorization
    new_auth = request.json

    if validate_user_credentials(auth):
        write_user_credentials(new_auth['new_username'], new_auth['new_password'])

        return jsonify({'message': 'Credentials changed successfully'}), 200
    
    else:
        return jsonify({'error': 'Unauthorized'}), 401
    
if __name__ == '__main__':
    app.run(debug=True, port=9091)