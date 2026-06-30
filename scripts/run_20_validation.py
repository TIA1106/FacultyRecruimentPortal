import json
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path for package imports
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

# Check USE_LAYOUT flag to pick output filename
USE_LAYOUT = os.environ.get('USE_LAYOUT', 'false').lower() == 'true'

from backend.app import parser as resume_parser
from backend.app import nlp_engine
from backend.app import ocr_engine

UPLOADS = ROOT / 'uploads'
OUT_DIR = ROOT / 'outputs'
OUT_DIR.mkdir(parents=True, exist_ok=True)

files = [p for p in UPLOADS.iterdir() if p.suffix.lower() == '.pdf']
if not files:
    print('No PDF files found in uploads/. Aborting.')
    raise SystemExit(1)

selected = files[:20]
results = []

for p in selected:
    fp = str(p)
    print('Processing', fp)
    parsed_file = resume_parser.parse_file(fp)
    entry = {
        'path': fp,
        'file_type': parsed_file.get('file_type'),
        'is_scanned': parsed_file.get('is_scanned'),
        'layout_used': False,
        'extraction_method': None,
        'parsed': None,
        'error': parsed_file.get('error')
    }

    raw_text = parsed_file.get('raw_text') or ''

    # Decide extraction method
    if parsed_file.get('error'):
        entry['extraction_method'] = 'error'
        results.append(entry)
        continue

    if parsed_file.get('is_scanned'):
        # Use OCR
        ocr_text = ocr_engine.extract_text_via_ocr(fp)
        raw_text = ocr_text
        entry['extraction_method'] = 'ocr'
    else:
        # digital text; parser may have already applied layout when configured
        entry['extraction_method'] = 'digital_layout' if len(raw_text.strip()) < 200 else 'digital'

    # run NLP parsing on the raw_text
    # If layout extraction was used, layout text may have spaced characters ("D r i s h t i").
    # Collapse common single-letter spacing sequences before NLP parsing.
    def _collapse_spaced_chars(text: str) -> str:
        import re
        # Be conservative: only collapse lines where a large fraction of tokens are single-character
        out_lines = []
        for line in text.splitlines():
            toks = line.split()
            if not toks:
                out_lines.append(line)
                continue
            single_frac = sum(1 for t in toks if len(t) == 1) / len(toks)
            digit_frac = sum(1 for t in toks if all(ch.isdigit() for ch in t)) / len(toks)
            # collapse if predominantly single-letter tokens (OCR spacing) or predominantly single digits (spaced numbers)
            if single_frac >= 0.6 or digit_frac >= 0.6:
                out_lines.append(''.join(toks))
            else:
                out_lines.append(line)
        return '\n'.join(out_lines)

    if os.environ.get('USE_LAYOUT', 'false').lower() == 'true' and raw_text:
        raw_text = _collapse_spaced_chars(raw_text)

    parsed = nlp_engine.parse_resume_text(raw_text)
    entry['parsed'] = parsed
    results.append(entry)

# Write results
outf_name = 'test_20_results_layout.json' if USE_LAYOUT else 'test_20_results.json'
outf = OUT_DIR / outf_name
with open(outf, 'w', encoding='utf-8') as fh:
    json.dump(results, fh, indent=2, ensure_ascii=False)

# Print a short summary
summary = {
    'total': len(results),
    'with_email': sum(1 for r in results if r.get('parsed') and r['parsed'].get('email')),
    'with_phone': sum(1 for r in results if r.get('parsed') and r['parsed'].get('phone')),
    'with_education': sum(1 for r in results if r.get('parsed') and r['parsed'].get('education')),
    'with_experience': sum(1 for r in results if r.get('parsed') and r['parsed'].get('experience')),
}
print('Wrote', outf)
print('Summary:', summary)
