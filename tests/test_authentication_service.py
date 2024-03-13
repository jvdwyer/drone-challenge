import unittest
from base64 import b64encode
from flask import Flask
from flask.testing import FlaskClient
from src.authentication_service import app, read_user_credentials, write_user_credentials, validate_user_credentials

class TokenServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = FlaskClient(self.app)
        write_user_credentials('admin', 'initial')

    def tearDown(self):
        write_user_credentials('admin', 'initial')

    def test_get_token_success(self):
        response = self.client.get('/get_token', headers={'Authorization': 'Basic YWRtaW46aW5pdGlhbA=='})
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', data)
        self.assertIn('expires_in', data)

    def test_validate_token_success(self):
        # Get a valid token (for testing purposes)
        get_token_response = self.client.get('/get_token', headers={'Authorization': 'Basic YWRtaW46aW5pdGlhbA=='})
        token = get_token_response.get_json()['token']

        # Validate the token
        validate_response = self.client.post('/validate_token', headers={'Authorization': token})
        validate_data = validate_response.get_json()

        self.assertEqual(validate_response.status_code, 200)
        self.assertIn('message', validate_data)
        self.assertEqual(validate_data['message'], 'Token is valid')

    def test_validate_token_expired(self):
        # Expired token (for testing purposes)
        expired_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNzEwMTk1NzIzfQ.k6OhmoADqreb1g6QMkkS3N8Gm5IiJYFW87CneScY99Y'

        # Validate the expired token
        validate_response = self.client.post('/validate_token', headers={'Authorization': expired_token})
        validate_data = validate_response.get_json()

        self.assertEqual(validate_response.status_code, 401)
        self.assertIn('error', validate_data)
        self.assertEqual(validate_data['error'], 'Token has expired')

    def test_validate_token_invalid(self):
        # Use an invalid token (for testing purposes)
        invalid_token = 'your_invalid_token_here'

        # Validate the invalid token
        validate_response = self.client.post('/validate_token', headers={'Authorization': invalid_token})
        validate_data = validate_response.get_json()

        self.assertEqual(validate_response.status_code, 401)
        self.assertIn('error', validate_data)
        self.assertEqual(validate_data['error'], 'Invalid token')

    def test_change_credentials_success(self):
         # Initial credentials
        initial_auth = 'admin:initial'

        # New credentials
        new_auth = {'new_username': 'new_user', 'new_password': 'new_password'}

        # Change credentials with initial authentication
        change_response = app.test_client().post('/change_credentials', json=new_auth, headers={'Authorization': 'Basic ' + b64encode(initial_auth.encode('utf-8')).decode('utf-8')})

        # Check response and updated credentials
        self.assertEqual(change_response.status_code, 200)
        updated_auth = read_user_credentials()
        self.assertEqual(updated_auth[0], new_auth['new_username'])
        self.assertEqual(updated_auth[1], new_auth['new_password'])
    
    def test_change_credentials_unauthorized(self):
        # Incorrect initial credentials
        initial_auth = ('wrong_user', 'wrong_password')

        # New credentials
        new_auth = {'new_username': 'new_user', 'new_password': 'new_password'}

        # Attempt to change credentials with incorrect initial authentication
        change_response = app.test_client().post('/change_credentials', json=new_auth, headers={'Authorization': 'Basic ' + b64encode(b'wrong_user:wrong_password').decode('utf-8')})

        # Check response and ensure credentials remain unchanged
        self.assertEqual(change_response.status_code, 401)
        unchanged_auth = read_user_credentials()
        self.assertEqual(unchanged_auth[0], 'admin')
        self.assertEqual(unchanged_auth[1], 'initial')

if __name__ == '__main__':
    unittest.main()