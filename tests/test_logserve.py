import pytest
import tempfile
import os
import json
from app import app

@pytest.fixture
def client():
    """Configures the app for testing and provides a test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Tests if the home route is accessible and returns the expected message."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"LogServe API is running!" in response.data

def test_upload_success(client):
    """Tests a successful file upload with correct counts."""
    # Create a temporary log file for the test
    temp_log_content = b"ERROR\nWARNING\nERROR"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=".log") as tmp_log:
        tmp_log.write(temp_log_content)
        temp_file_path = tmp_log.name
    
    # Simulate a file upload
    with open(temp_file_path, 'rb') as f:
        data = {'file': (f, 'test.log')}
        response = client.post('/upload', data=data)

    # Clean up the temporary file
    os.remove(temp_file_path)

    # Assert the response
    assert response.status_code == 200
    
    # Decode the JSON response and check the value
    response_data = json.loads(response.data)
    assert response_data['line_count'] == 3
    assert response_data['message'] == "File 'test.log' processed successfully"

def test_upload_no_file_part(client):
    response = client.post('/upload', data={})
    assert response.status_code == 400
    assert b"No file part in the request" in response.data

def test_upload_disallowed_file_type(client):
    with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
    with open(tmp_file_path, 'rb') as f:
        data = {'file': (f, 'malicious.exe')}
        response = client.post('/upload', data=data)
    os.remove(tmp_file_path)
    assert response.status_code == 400
    assert b"Disallowed file type." in response.data

def test_upload_empty_filename(client):
    """Tests a file with an empty filename."""
    # We will create a temp file and write to it
    _, tmp_file_path = tempfile.mkstemp()
    
    # We open it for reading and writing and simulate the upload
    with open(tmp_file_path, 'rb') as f:
        data = {'file': (f, '')}
        response = client.post('/upload', data=data)

    # Clean up the file
    os.remove(tmp_file_path)

    assert response.status_code == 400
    assert b"No selected file" in response.data