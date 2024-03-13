from flask import Flask, request, jsonify
import jwt
import datetime
import json
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'

CONFIG_FILE_PATH = 'config/application_settings.json'

# Reads user credentials from application_settings
def read_user_credentials():
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            config_data = json.load(config_file)
            user_data = config_data.get('authentication_service', {}).get('username'), config_data.get('authentication_service', {}).get('password')
            return user_data
    return None

# Writes user credentials to application_settings
def write_user_credentials(username, password):
    config_data = {'authentication_service': {'port': 9091, 'username': username, 'password': password}}

    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            existing_config = json.load(config_file)
            existing_config.update(config_data)
            config_data = existing_config

    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(config_data, config_file)

# Confirms supplied user credentials match actual
def validate_user_credentials(auth):
    user_credentials = read_user_credentials()

    if auth and auth.username == user_credentials[0] and auth.password == user_credentials[1]:
        return True
    else:
        return False

# Route returns token to valid calling clients
@app.route('/get_token', methods=['GET'])
def get_token():
    auth = request.authorization

    if validate_user_credentials(auth):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        
        token = jwt.encode({'username': auth.username, 'exp': expiration_time}, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token, 'expires_in': 3600})
    else:
        return jsonify({'error': 'Unauthorized'}), 401

# Route validates tokens
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

# Route changes credentials for valid calling clients    
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
    with open(CONFIG_FILE_PATH, 'r') as config_file:
        config_data = json.load(config_file)
        port = config_data.get('authentication_service', {}).get('port')
    app.run(debug=True, port=port)