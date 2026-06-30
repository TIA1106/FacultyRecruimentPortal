import sys, io, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/Faculty Recruitment Portal')

from backend.app.parser import parse_file
from backend.app.ocr_engine import extract_text_via_ocr
from backend.app.nlp_engine import parse_resume_text
from backend.app.pdf_generator import generate_candidate_pdf
import os

files = ['312b8a08_20200608Reshma.pdf', '05bda005_SureshN.pdf']

for fname in files:
    path = f'd:/Faculty Recruitment Portal/uploads/{fname}'
    print(f"=== Testing {fname} ===")
    try:
        print("1. Parsing file...")
        parsed = parse_file(path)
        is_scanned = parsed['is_scanned']
        if is_scanned:
            print("   -> Scanned, running OCR...")
            text = extract_text_via_ocr(path)
        else:
            print("   -> Digital PDF.")
            text = parsed['raw_text']
            
        print("2. NLP Extraction...")
        data = parse_resume_text(text)
        print(f"   Name: {data.get('name')}")
        print(f"   Email: {data.get('email')}")
        print(f"   Edu count: {len(data.get('education', []))}")
        print(f"   Exp count: {len(data.get('experience', []))}")
        
        print("3. Generating PDF...")
        out_path = f"d:/Faculty Recruitment Portal/test_output_{fname}"
        generate_candidate_pdf(data, out_path)
        print("   -> SUCCESS!")
    except Exception as e:
        print(f"!!! CRASH in {fname} !!!")
        traceback.print_exc()
    print()
