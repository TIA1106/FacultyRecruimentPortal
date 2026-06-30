import os
from pathlib import Path
from backend.app.layout_parser import extract_text_with_layout

ROOT = Path.cwd()
UPLOADS = ROOT / 'uploads'
OUT_DIR = ROOT / 'outputs' / 'layout_texts'
OUT_DIR.mkdir(parents=True, exist_ok=True)

files = list(UPLOADS.glob('*'))
if not files:
    print('No files in uploads/ to process')

count = 0
for p in files:
    if p.suffix.lower() != '.pdf':
        continue
    try:
        if p.suffix.lower() == '.pdf':
            txt = extract_text_with_layout(str(p), use_layoutparser=False)
        

        outp = OUT_DIR / (p.stem + '.txt')
        with open(outp, 'w', encoding='utf-8') as fh:
            fh.write(txt or '')
        count += 1
        print('Wrote', outp)
    except Exception as e:
        print('Error processing', p, e)

print('Processed', count, 'files')
