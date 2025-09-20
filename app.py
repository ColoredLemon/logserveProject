import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename # NEW: Import secure_filename
from parser import count_lines

# Your existing code for loading environment variables
load_dotenv()
log_level = os.getenv('LOG_LEVEL', 'INFO')
numeric_log_level = getattr(logging, log_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_log_level, format='%(asctime)s - %(levelname)s - %(message)s')



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