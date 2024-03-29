from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
import geopy.distance
import requests
import json
import csv
import certifi
import ssl

app = Flask(__name__)

# Constants
CONFIG_FILE_PATH = 'config/application_settings.json'
CSV_FILE_PATH = 'test.csv'
DRONE_RANGE = 25

# Global
remaining_range = DRONE_RANGE

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

# Returns GPS coordinates of an address
def get_coordinates(address):
    # Sets default ssl context for geopy use
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    
    geolocator = Nominatim(user_agent='routing')
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

# Returns store location in GPS
def get_store_location():
    with open (CONFIG_FILE_PATH, 'r') as config_file:
        config_data = json.load(config_file)
        address = config_data.get('routing_service', {}).get('home_address')
        return get_coordinates(address)
    
# Returns the next destination
def find_next_destination(current_location, orders):
    global remaining_range
    
    for order in orders:
        order_location = get_coordinates(order['address'])
        distance_to_order = geopy.distance.geodesic(current_location, order_location)
        if (distance_to_order <= remaining_range):
            return {'order_time': order['order_time'], 'address': order['address']}
    return {'order_time': None, 'address': 'Back to store'}

def calculate_distance(location1, location2):
    return geopy.distance.geodesic(location1, location2)

def calculate_priority(order):
    return['order_time']

# More global    
HOME_ADDRESS = get_store_location()
AUTH_SERVICE_URL = f'http://localhost:{get_service_port('authentication_service')}'

# Route returns next destination
@app.route('/get_destination', methods=['GET'])
def get_destination():
    token = request.authorization.token

    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    
    auth_response = requests.post(
        f'{AUTH_SERVICE_URL}/validate_token',
        headers = {'Authorization': token}
    )

    if auth_response.status_code == 200:
        global remaining_range
        
        current_location = request.args.get('current_location', default=None)
        if current_location:
            current_location = tuple(map(float, current_location.split(',')))
        else:
            current_location = HOME_ADDRESS
        
        distance_to_home = calculate_distance(current_location, HOME_ADDRESS)
        
        orders = read_csv()
        
        # Sort orders by time
        orders.sort(key=lambda x: calculate_priority(x))
        
        # Create list of orders the drone can reach
        reachable_orders = []
        for order in orders:
            order_location = get_coordinates(order['address'])
            distance_to_order = calculate_distance(current_location, order_location)
            if distance_to_order <= remaining_range + distance_to_home:
                reachable_orders.append({'order_time': order['order_time'], 'address': order['address'], 'distance': distance_to_order})
        
        # Sort reachable orders by distance
        reachable_orders.sort(key=lambda x: x['distance'])
        
        # Select closest reachable order or send drone home
        if reachable_orders:
            next_destination = reachable_orders[0]
            destination_coordinates = get_coordinates(next_destination['address'])
            remaining_range -= next_destination['distance'].miles
        else:
            destination_coordinates = get_coordinates(HOME_ADDRESS)
            remaining_range = DRONE_RANGE
        return jsonify(destination_coordinates), 200

    else:
        return jsonify({auth_response.request.body}), auth_response.status_code
    
if __name__ == '__main__':
    app.run(debug=True, port=get_service_port())
