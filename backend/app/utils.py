import os
import uuid
from werkzeug.utils import secure_filename

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # d:\Faculty Recruitment Portal\backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)                              # d:\Faculty Recruitment Portal

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, 'outputs')
DATASETS_FOLDER = os.path.join(PROJECT_ROOT, 'data')

# Allowed extensions (PDF only)
ALLOWED_EXTENSIONS = {'pdf'}

# Fixed schema format
FIXED_SCHEMA = {
    "name": "",
    "headline": "",
    "location": "",
    "email": "",
    "phone": "",
    "summary": "",
    "links": [],
    "education": [],
    "skills": [],
    "experience": [],
    "publications": [],
    # Additional fields for richer academic/professional profiles
    "projects": [],
    "achievements": [],
    "certificates": [],
    "awards": [],
    "involvement": [],
    # Faculty-specific sections
    "memberships": [],
    "administrative_works": [],
    "workshops": [],
    # New specific fields for institutional faculty application form
    "advt_no": "",
    "registration_no": "",
    "post_applied_for": "",
    "specialisation": "",
    "dob": "",
    "age": "",
    "father_name": "",
    "mother_name": "",
    "nationality": "",
    "place_of_birth": "",
    "gender_marital_status": "",
    "category": "",
    "religion": "",
    "husband_name": "",
    "other_category": "",
    "thesis_info": [],
    "referees": []
}

def init_directories():
    """Ensure upload and output folders exist."""
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file is PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save upload file securely with a unique identifier to avoid collisions."""
    init_directories()
    if file and allowed_file(file.filename):
        original_name = secure_filename(file.filename)
        # Prepend unique ID to filename
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{unique_id}_{original_name}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filepath
    return None

def normalize_extracted_data(data):
    """Ensure returning dictionary aligns exactly with fixed schema."""
    normalized = {}
    for key, default in FIXED_SCHEMA.items():
        val = data.get(key)
        if val is None:
            normalized[key] = default
        else:
            if isinstance(default, list):
                if isinstance(val, list):
                    normalized[key] = [item for item in val if item]
                elif isinstance(val, str):
                    normalized[key] = [val] if val else []
                else:
                    normalized[key] = []
            else:
                normalized[key] = str(val).strip()
    return normalized
