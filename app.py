import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import Config
from blueprints.main_routes import main as main_blueprint
from dotenv import load_dotenv

# Your existing code for loading environment variables
load_dotenv()
log_level = os.getenv('LOG_LEVEL', 'INFO')
numeric_log_level = getattr(logging, log_level.upper(), logging.INFO)

# Create the Flask application instance
app = Flask(__name__)
app.config.from_object(Config)

# Set up global logging to a file
log_file_path = os.path.join(os.getcwd(), 'logs', 'app.log')
log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a rotating file handler that logs to app.log and rotates
# after 1MB, keeping up to 5 backup files.
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(numeric_log_level)
app.logger.addHandler(file_handler)
app.logger.setLevel(numeric_log_level)

# Register the blueprint
app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    app.run(debug=True)