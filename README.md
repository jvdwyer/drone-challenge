# Drone challenge

## Introduction

Services that provide authentication and next destination to a drone client delivering pizza.

## Installation

To use the services, you'll need to install the required Python packages. You can do this using 'pip3'. The the following command in your terminal:

```bash
pip install -r requirements.txt
```

This will install the necessary dependencies for the services.

## Usage

### Run the Service
To start the Authentication service locally, run the following command:
```bash
python run_services.py
```

### Fleet Manager Service
Coming shortly! This service will provide a client its next destination in GPS coordinates upon request.

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
* Description: validate the provided token.
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