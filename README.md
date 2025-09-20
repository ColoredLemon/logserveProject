logserve.py - A Log Analysis API
logserve.py is a simple, secure web API built with Python and Flask. It is designed to receive and analyze log files via HTTP requests, counting key metrics and returning the results as a JSON response.

📝 Features
Secure File Upload: Accepts files via a POST request to the /upload endpoint.

Automated Analysis: Processes .log and .csv files to count lines.

JSON Response: Returns a clean, structured JSON object with the results.

🛡️ Security Sanity Sweep
The API has been hardened against common vulnerabilities with the following checks:

File Size Limit: Rejects files that exceed a configurable size limit to prevent Denial of Service (DoS) attacks.

Secure Filename: Uses werkzeug.utils.secure_filename to sanitize all uploaded filenames, preventing Directory Traversal attacks.

File Extension Check: Only allows specific file types (.log and .csv) to be uploaded, mitigating the risk of executing malicious code.

🛠️ Installation
To set up the project, you'll need Python 3.10 or higher.

Clone the repository and navigate into the project directory.

Create a virtual environment:

Bash

python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install dependencies:

Bash

pip install -r requirements.txt
🚀 Usage
The API has two routes: a home route and an upload route.

GET /: Returns a status message to confirm the API is running.

POST /upload: Accepts a file via a multipart form and returns a JSON response.

Example with curl:

Bash

curl -X POST -F "file=@your-file.log" http://127.0.0.1:5000/upload

This part is for the merging test I am practicing on git/github.