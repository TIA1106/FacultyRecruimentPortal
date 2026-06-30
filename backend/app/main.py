import os
import sys
import io
import subprocess
from flask import Flask

# Fix for Windows UnicodeEncodeError on print statements
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.routes import register_routes
from backend.app.utils import init_directories, UPLOAD_FOLDER

def ensure_spacy_model():
    """Verify if the spaCy English model is installed, and download it if missing."""
    try:
        import spacy
        if not spacy.util.is_package("en_core_web_sm"):
            print("spaCy English model 'en_core_web_sm' not found. Downloading...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            print("spaCy model downloaded successfully.")
        else:
            print("spaCy model 'en_core_web_sm' is already installed.")
    except Exception as e:
        print(f"Warning: Could not verify or download spaCy model: {e}")

def create_app():
    # Set templates and static folder paths relative to this file
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Configure Flask Upload folder and size limit (16MB)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    # Ensure directories exist
    init_directories()
    
    # Register endpoints
    register_routes(app)
    
    return app

if __name__ == '__main__':
    # Ensure spaCy model exists before running the app
    ensure_spacy_model()
    
    app = create_app()
    print("Starting Flask application on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
