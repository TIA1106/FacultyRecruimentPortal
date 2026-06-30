import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/Faculty Recruitment Portal')
from backend.app.parser import parse_file
from backend.app.nlp_engine import parse_resume_text

# The user said Tia Sukhnanni's resume - check recent uploads
for fname in ['37f3a6d0_Doc1.pdf', 'caa33fc9_Doc1.pdf']:
    try:
        parsed = parse_file(f'd:/Faculty Recruitment Portal/uploads/{fname}')
        scanned = parsed['is_scanned']
        txt = parsed['raw_text']
        print(f'{fname}: is_scanned={scanned}, text_len={len(txt)}')
        if txt:
            print('First 300 chars:', repr(txt[:300]))
        print()
    except Exception as e:
        print(f'{fname}: ERROR - {e}')
        print()
