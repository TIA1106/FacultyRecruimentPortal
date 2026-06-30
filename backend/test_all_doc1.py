import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/Faculty Recruitment Portal')

from backend.app.parser import parse_file
from backend.app.ocr_engine import extract_text_via_ocr, TESSERACT_AVAILABLE
from backend.app.nlp_engine import parse_resume_text
from backend.app.pdf_generator import generate_candidate_pdf
import os, glob

print(f"Tesseract available: {TESSERACT_AVAILABLE}")
print()

# Test ALL Doc1 files
doc1_files = sorted(glob.glob('d:/Faculty Recruitment Portal/uploads/*Doc1.pdf'))
for fname in doc1_files:
    bn = os.path.basename(fname)
    print(f"=== {bn} ===")
    parsed = parse_file(fname)
    scanned = parsed['is_scanned']
    raw_len = len(parsed['raw_text'])
    print(f"  is_scanned={scanned}, raw_text len={raw_len}")
    
    if scanned:
        ocr_text = extract_text_via_ocr(fname)
        text = ocr_text or ''
        method = 'OCR'
    else:
        text = parsed['raw_text']
        method = 'Digital'
    
    print(f"  Method: {method}, text_len={len(text)}")
    if text:
        data = parse_resume_text(text)
        print(f"  Name: {data.get('name')}")
        print(f"  DOB: {data.get('dob')}")
        print(f"  Age: {data.get('age')}")
        print(f"  Email: {data.get('email')}")
        edu = data.get('education', [])
        print(f"  Education count: {len(edu)}")
        for e in edu[:2]:
            print(f"    - {e}")
    else:
        print("  ERROR: No text extracted!")
    print()
