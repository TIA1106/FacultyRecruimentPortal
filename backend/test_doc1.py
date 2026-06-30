import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/Faculty Recruitment Portal')

from backend.app.parser import parse_file
from backend.app.ocr_engine import extract_text_via_ocr, TESSERACT_AVAILABLE
from backend.app.nlp_engine import parse_resume_text
from backend.app.pdf_generator import generate_candidate_pdf
import os

print(f"Tesseract available: {TESSERACT_AVAILABLE}")
print()

# Test Doc1 (scanned)
fname = 'd:/Faculty Recruitment Portal/uploads/37f3a6d0_Doc1.pdf'
print(f"=== Testing: {os.path.basename(fname)} ===")
parsed = parse_file(fname)
print(f"is_scanned: {parsed['is_scanned']}")
print(f"raw_text len: {len(parsed['raw_text'])}")
print(f"error: {parsed.get('error')}")
print()

if parsed['is_scanned']:
    print("Running OCR...")
    ocr_text = extract_text_via_ocr(fname)
    print(f"OCR text length: {len(ocr_text) if ocr_text else 0}")
    if ocr_text:
        print("First 800 chars of OCR text:")
        print(ocr_text[:800])
        print("...")
        print()
        data = parse_resume_text(ocr_text)
        print(f"Name: {data.get('name')}")
        print(f"DOB: {data.get('dob')}")
        print(f"Age: {data.get('age')}")
        print(f"Email: {data.get('email')}")
        print(f"Phone: {data.get('phone')}")
        print(f"Education count: {len(data.get('education', []))}")
        for e in data.get('education', []):
            print(f"  - {e}")
        
        # Generate PDF
        out = 'd:/Faculty Recruitment Portal/test_doc1_scanned.pdf'
        generate_candidate_pdf(data, out)
        print(f"\nPDF generated: {out}")
        print(f"PDF size: {os.path.getsize(out)} bytes")
    else:
        print("ERROR: OCR returned empty text!")
else:
    print("Not scanned - using raw text")
    data = parse_resume_text(parsed['raw_text'])
    print(f"Name: {data.get('name')}")
