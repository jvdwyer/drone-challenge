# Drone challenge

## Introduction

Services that provide authentication and next destination to a drone client delivering pizza.

## Installation

To use the services, you'll need to install the required Python packages. You can do this using 'pip'. Run the following command in your terminal:

```bash
pip install -r requirements.txt
```

This will install the necessary dependencies for the services.

## Usage

### Run the Service
To start the services locally, run the following command:
```bash
python run_services.py
```

### Routing Service
This service provides calling clients (pizza delivery drones) the next destination they should travel to. A simple heuristic algorithm looking at orders within battery range (including return home trip) and order time is implemented to determine the next location. It uses geopy to translate address into GPS coordinates and calculate distance between locations. It also tracks how much range the drone has remaining. It runs on port 9092 by default.

#### Routing Service Endpoints
##### Get Destination
* Endpoint: '/get_destination
* Method: 'GET'
* Description: Get next destination for drone
* Example Request:
```bash
curl -X GET -H "Authorization: <token>" http://localhost:9092/get_destination
```

### Authentication Service
This service provides token based authentication allowing clients to obtain tokens and change their credentials securely. It runs on port 9091 by default.

#### Authentication Service Endpoints
##### Get Token:
* Endpoint: '/get_token'
* Method: 'GET'
* Description: Obtain a token by providing valid credentials.
* Example Request:
```bash
curl -X GET -u admin:initial http://localhost:9091/get_token
```
Replace username and password with your desired credentials.

##### Validate Token:
* Endpoint: '/validate_token'
* Method: 'POST'
* Description: Validate the provided token.
* Example Request:
```bash
curl -X POST -H "Authorization: <token>" http://localhost:9091/validate_token
```

Replace <token> with the obtained token.

##### Change Credentials:
* Endpoint: '/change_credentials'
* Method: 'Post'
* Description: Change the username and password.
* Example Request:
```Bash
curl -X POST -H "Authorization: Basic YWRtaW46aW5pdGlhbA==" -H "Content-Type: application/json" -d '{"new_username": "new_user", "new_password": "new_password"}' http://localhost:9091/change_credentials
```

Replace <token> with the obtained token and adjust the new credentials as needed.

#### Unit Tests
Use the following command to run the unit tests

```bash
python -m unittest tests/test_authentication_service.py
```