import fitz  # PyMuPDF
import os
from backend.app.cleaner import clean_text
from backend.app.layout_parser import extract_text_with_layout, extract_faculty_form_fields
import os as _os



def is_pdf_scanned(filepath):
    """
    Open PDF and check if it contains any digital text.
    Returns: (is_scanned, extracted_text)
    - If there is searchable text, is_scanned = False and returns the text.
    - If no searchable text is found, is_scanned = True and extracted_text = "".
    """
    try:
        doc = fitz.open(filepath)
        text_content = []
        total_text_len = 0
        
        for page in doc:
            text = page.get_text()
            if text:
                text_content.append(text)
                total_text_len += len(text.strip())
                
        doc.close()
        
        # If the total searchable text is very small (less than 50 chars), classify as scanned
        if total_text_len < 50:
            return True, ""
        return False, "\n".join(text_content)
    except Exception as e:
        print(f"Error checking PDF type for {filepath}: {e}")
        # Default to scanned if we fail to read it, so it tries OCR
        return True, ""

def parse_file(filepath):
    """
    Detect file type and extract raw text or route to OCR.
    Returns:
    {
        "file_type": "pdf" | "docx" | "unknown",
        "is_scanned": bool,
        "raw_text": str,  # Empty if scanned
        "layout_fields": dict,  # Optional layout-aware field hints for form-style PDFs
        "error": str | None
    }
    """
    if not os.path.exists(filepath):
        return {
            "file_type": "unknown",
            "is_scanned": False,
            "raw_text": "",
            "layout_fields": {},
            "error": "File does not exist"
        }
        
    ext = filepath.rsplit('.', 1)[1].lower() if '.' in filepath else ''

    # Support PDFs only
    if ext != 'pdf':
        return {
            "file_type": "unknown",
            "is_scanned": False,
            "raw_text": "",
            "layout_fields": {},
            "error": f"Unsupported file extension: {ext}. Only PDF files are accepted."
        }

    if ext == 'pdf':
        is_scanned, text = is_pdf_scanned(filepath)
        # Config: if USE_LAYOUT environment variable set to 'true', prefer layout-aware extraction
        use_layout = _os.environ.get('USE_LAYOUT', 'false').lower() == 'true'

        # If scanned, return scanned flag so caller can use OCR. If digital but very short,
        # attempt layout-aware extraction (helps multi-column or table resumes).
        if is_scanned:
            return {
                "file_type": "pdf",
                "is_scanned": True,
                "raw_text": "",
                "layout_fields": {},
                "error": None
            }
        else:
            layout_fields = {}
            # If layout parsing requested or extracted text is very short, try layout-aware extraction
            if use_layout or (isinstance(text, str) and len(text.strip()) < 200):
                try:
                    lp_text = extract_text_with_layout(filepath, use_layoutparser=False)
                    if lp_text and lp_text.strip():
                        cleaned = clean_text(lp_text)
                        try:
                            layout_fields = extract_faculty_form_fields(filepath)
                        except Exception as e:
                            print(f"Layout field extraction failed for {filepath}: {e}")
                        return {
                            "file_type": "pdf",
                            "is_scanned": False,
                            "raw_text": cleaned,
                            "layout_fields": layout_fields,
                            "error": None
                        }
                except Exception as e:
                    # fallback to original digital text if layout parser fails
                    print(f"Layout parsing failed for {filepath}: {e}")

            cleaned = clean_text(text)
            try:
                layout_fields = extract_faculty_form_fields(filepath)
            except Exception as e:
                print(f"Layout field extraction failed for {filepath}: {e}")
            return {
                "file_type": "pdf",
                "is_scanned": False,
                "raw_text": cleaned,
                "layout_fields": layout_fields,
                "error": None
            }
            
    else:
        return {
            "file_type": "unknown",
            "is_scanned": False,
            "raw_text": "",
            "layout_fields": {},
            "error": f"Unsupported file extension: {ext}"
        }
