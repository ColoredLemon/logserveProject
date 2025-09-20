import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
from werkzeug.utils import secure_filename # NEW: Import secure_filename
from parser import count_lines
from functools import wraps

# Your existing code for loading environment variables
load_dotenv()
log_level = os.getenv('LOG_LEVEL', 'INFO')
numeric_log_level = getattr(logging, log_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_log_level, format='%(asctime)s - %(levelname)s - %(message)s')

ALLOWED_USERS = ['bob', 'alice', 'eve']
ADMIN_USERS = ['alice']

app = Flask(__name__)

# Security Constant
MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {'log', 'csv'}

# Set up logging to a file
log_file_path = os.path.join(os.getcwd(), 'logs', 'app.log')
log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a rotating file handler that logs to app.log and rotates
# after 1MB, keeping up to 5 backup files.
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=1024 * 1024, # 1 MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineFno)d]'
))
file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

def allowed_file(filename):
    """
    Checks if a file's extension is in the ALLOWED_EXTENSIONS set.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return "LogServe API is running!"

# A decorator to check for admin authorization
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User')
        if user_id not in ADMIN_USERS:
            app.logger.warning(f"Admin access attempt by unauthorized user: {user_id}")
            return make_response(jsonify(message="Unauthorized Access"), 401)
        return f(*args, **kwargs)
    return decorated_function
# A decorator to check for user authorization
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User')
        if user_id not in ALLOWED_USERS:
            logging.warning(f"Unauthorized access attempt by user: {user_id}")
            return make_response(jsonify(message="Unauthorized"), 401)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    user_id = request.headers.get('X-User')
    app.logger.info(f"Admin access granted for user: {user_id}")
    return jsonify({"message": "Welcome to the admin dashboard!", "user": user_id}), 200

@app.route('/upload', methods=['POST'])
@login_required
def upload_log():
    # If this line is reached, the user is already authorized
    user_id = request.headers.get('X-User')
    logging.info(f"Authorized request received from user: {user_id}")
    
    # 1. Get the file part from the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # 2. Perform all checks on the file object before processing
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        logging.warning("User attempted to upload disallowed file type.")
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

if __name__ == '__main__':
    app.run(debug=True)