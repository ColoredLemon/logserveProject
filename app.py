import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename # NEW: Import secure_filename

# Your existing code for loading environment variables
load_dotenv()
log_level = os.getenv('LOG_LEVEL', 'INFO')
numeric_log_level = getattr(logging, log_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_log_level, format='%(asctime)s - %(levelname)s - %(message)s')

# You'll need to copy parser.py into this directory
from parser import count_lines

app = Flask(__name__)

# Security Constant
MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {'log', 'csv'}

def allowed_file(filename):
    """
    Checks if a file's extension is in the ALLOWED_EXTENSIONS set.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return "LogServe API is running!"

@app.route('/upload', methods=['POST'])
def upload_log():
    # 1. SECURITY CHECK: Check file size first
    if request.content_length and request.content_length > MAX_FILE_SIZE_MB * 1024 * 1024:
        logging.warning("User attempted to upload file exceeding size limit.")
        return jsonify({"error": f"File is too large. Max size is {MAX_FILE_SIZE_MB} MB."}), 413

    # 2. CHECK: Check if a file part was provided
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # 3. CHECK: Check for empty filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # SECURITY: Sanitize the filename to prevent path traversal (NEW)
        sanitized_filename = secure_filename(file.filename)
        
        # Save the file to a temporary location using the sanitized filename
        temp_filepath = os.path.join('/tmp', sanitized_filename)
        file.save(temp_filepath)
    
        # 4. SECURITY CHECK: Check for allowed file type
    if not allowed_file(file.filename):
        logging.warning("User attempted to upload disallowed file type.")
        return jsonify({"error": "Disallowed file type."}), 400

    if file:
        # Save the file to a temporary location
        temp_filepath = os.path.join('/tmp', file.filename)
        file.save(temp_filepath)
        
        # Call your logparse function on the temporary file
        line_count, error_msg = count_lines(temp_filepath)

        # Remove the temporary file
        os.remove(temp_filepath)

        if error_msg:
            return jsonify({"error": error_msg}), 500
        
        return jsonify({"message": f"File '{file.filename}' processed successfully", "line_count": line_count}), 200

    return jsonify({"error": "An unknown error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)