import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/Faculty Recruitment Portal')

from backend.app.parser import parse_file
from backend.app.nlp_engine import parse_resume_text
from backend.app.pdf_generator import generate_candidate_pdf
import os

# Test with the most recent INF010008 uploads
for fname in ['862069fd_INF010008.pdf', 'd65e6c9d_INF010008.pdf', '28297f9d_INF010008.pdf']:
    try:
        path = f'd:/Faculty Recruitment Portal/uploads/{fname}'
        parsed = parse_file(path)
        scanned = parsed['is_scanned']
        txt = parsed['raw_text']
        print(f'{fname}:')
        print(f'  is_scanned={scanned}')
        print(f'  raw_text len={len(txt)}')
        if txt:
            data = parse_resume_text(txt)
            print(f'  Name: {data.get("name")}')
            print(f'  DOB: {data.get("dob")}')
            print(f'  Age: {data.get("age")}')
            edu = data.get('education', [])
            print(f'  Edu count: {len(edu)}')
            for e in edu[:3]:
                print(f'    - {e}')
        print()
    except Exception as ex:
        print(f'{fname}: ERROR {ex}')
        import traceback
        traceback.print_exc()
        print()
