from functools import wraps
from flask import Blueprint, jsonify, request, make_response, current_app
import os
from werkzeug.utils import secure_filename
from parser import count_lines

main = Blueprint('main', __name__)

def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# This is the decorator you will use on your routes
def secure_headers_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        # Ensure the response is a Flask Response object
        if not isinstance(response, (str, tuple)):
            response_obj = response
        else:
            response_obj = current_app.make_response(response) # Assuming 'app' is in scope
        
        # Call the header function
        return add_security_headers(response_obj)
    return decorated_function

def allowed_file(filename):
    """
    Checks if a file's extension is in the ALLOWED_EXTENSIONS set.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def middleware_logger(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.info(f"Request by user: {request.headers.get('X-User')} to endpoint: {request.path} using method: {request.method}")

        response = f(*args, **kwargs)
        
        # Ensure the response is a Flask Response object before trying to log its status code.
        if not isinstance(response, (str, tuple)):
            response_obj = response
        else:
            response_obj = current_app.make_response(response)

        current_app.logger.info(f"Response status: {response_obj.status_code}")

        return response_obj
    return decorated_function

@main.route('/')
@secure_headers_decorator
@middleware_logger
def home():
    return "LogServe API is running!"

# A decorator to check for admin authorization
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User')
        if user_id not in current_app.config['ADMIN_USERS']:
            current_app.logger.warning(f"Admin access attempt by unauthorized user: {user_id}")
            return make_response(jsonify(message="Unauthorized Access"), 401)
        return f(*args, **kwargs)
    return decorated_function
# A decorator to check for user authorization
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User')
        if user_id not in current_app.config['ALLOWED_USERS']:
            current_app.logger.warning(f"Unauthorized access attempt by user: {user_id}")
            return make_response(jsonify(message="Unauthorized"), 401)
        return f(*args, **kwargs)
    return decorated_function

@main.route('/admin_dashboard')
@secure_headers_decorator
@middleware_logger
@admin_required
def admin_dashboard():
    user_id = request.headers.get('X-User')
    current_app.logger.info(f"Admin access granted for user: {user_id}")
    return jsonify({"message": "Welcome to the admin dashboard!", "user": user_id}), 200

@main.route('/upload', methods=['POST'])
@secure_headers_decorator
@middleware_logger
@login_required
def upload_log():
    # If this line is reached, the user is already authorized
    user_id = request.headers.get('X-User')
    current_app.logger.info(f"Authorized request received from user: {user_id}")
    
    # 1. Get the file part from the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # 2. Perform all checks on the file object before processing
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        current_app.logger.warning("User attempted to upload disallowed file type.")
        return jsonify({"error": "Disallowed file type."}), 400
    
    # 3. Process the file only if all checks pass
    #    (The if request.content_length check is handled by Flask's config)
    #    (The code that was here before is now the only place file is handled)
    
    # 4. Save the file to a temporary location using the sanitized filename
    sanitized_filename = secure_filename(file.filename)
    temp_filepath = os.path.join('/tmp', sanitized_filename)
    file.save(temp_filepath)

    # 5. Call your logparse function on the temporary file
    line_count, error_msg = count_lines(temp_filepath)
    
    # 6. Remove the temporary file
    os.remove(temp_filepath)

    if error_msg:
        return jsonify({"error": error_msg}), 500
    
    return jsonify({"message": f"File '{sanitized_filename}' processed successfully", "line_count": line_count}), 200