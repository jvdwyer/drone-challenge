from flask import Flask, request, jsonify
import requests
import json
import csv

app = Flask(__name__)

CONFIG_FILE_PATH = 'config/application_settings.json'
CSV_FILE_PATH = 'test.csv'

# Reads CSV
def read_csv():
    data = []
    with open(CSV_FILE_PATH, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

# Returns service port
def get_service_port(service_name='routing_service'):
    # Read port from application settings
    with open(CONFIG_FILE_PATH, 'r') as config_file:
        config_data = json.load(config_file)
        port = config_data.get(service_name, {}).get('port')
        return port

AUTH_SERVICE_URL = f'http://localhost:{get_service_port('authentication_service')}'

# Route returns next destination
@app.route('/get_destination', methods=['GET'])
def get_destination():
    token = request.authorization.token

    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    
    auth_response = requests.post(AUTH_SERVICE_URL + '/validate_token', headers = {'Authorization': token})

    if auth_response.status_code == 200:
        ## TODO serve next destination
        data = read_csv()
        return jsonify(data), 200
    else:
        return jsonify({auth_response.request.body}), auth_response.status_code
    
if __name__ == '__main__':
    app.run(debug=True, port=get_service_port())
