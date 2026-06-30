import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from backend.app import parser as resume_parser
from backend.app import nlp_engine
from backend.app import ocr_engine

p = ROOT / 'uploads' / '39bb395b_Naman_Reume.pdf'
if not p.exists():
    print('File not found:', p)
    sys.exit(1)
fp = str(p)
print('Processing', fp)
res = resume_parser.parse_file(fp)
print('\n=== PARSE FILE METADATA ===')
for k in ['file_type','is_scanned','error']:
    print(k+':', res.get(k))
raw = res.get('raw_text') or ''
print('\n=== RAW TEXT (first 1200 chars) ===')
print(raw[:1200])

print('\n=== Running NLP parse_resume_text() ===')
parsed = nlp_engine.parse_resume_text(raw)
import json
print(json.dumps(parsed, indent=2, ensure_ascii=False)[:2000])

print('\n--- Projects field ---')
print(parsed.get('projects'))
print('\n--- Confidence summary ---')
print(parsed.get('confidence'))

# If layout text exists in outputs/layout_texts, print small snippet
layout_fp = ROOT / 'outputs' / 'layout_texts' / (p.stem + '.txt')
if layout_fp.exists():
    print('\n=== LAYOUT TEXT (first 1000 chars) ===')
    print(layout_fp.read_text(encoding='utf-8')[:1000])
else:
    print('\nNo layout text file found for this PDF.')
