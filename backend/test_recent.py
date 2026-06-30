import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/Faculty Recruitment Portal')

from backend.app.parser import parse_file
from backend.app.nlp_engine import parse_resume_text

# Test with the recent resume_14 and resume_16
for fname in ['8cda388a_resume_14.pdf', 'b59b8dea_resume_16.pdf']:
    try:
        parsed = parse_file(f'd:/Faculty Recruitment Portal/uploads/{fname}')
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
            for e in edu:
                print(f'    - {e}')
        print()
    except Exception as ex:
        print(f'{fname}: ERROR {ex}')
        import traceback
        traceback.print_exc()
        print()
