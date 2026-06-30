"""
Comprehensive 50+ Resume Test Suite
Tests both scanned & digital PDFs through the full pipeline:
extraction → NLP → PDF generation.
Reports pass/fail, missing fields, and quality scores.
"""
import sys, io, os, glob, time, json, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'd:/Faculty Recruitment Portal')

from backend.app.parser import parse_file
from backend.app.ocr_engine import extract_text_via_ocr, TESSERACT_AVAILABLE
from backend.app.nlp_engine import parse_resume_text
from backend.app.pdf_generator import generate_candidate_pdf

UPLOADS = 'd:/Faculty Recruitment Portal/uploads'
OUTPUT_DIR = 'd:/Faculty Recruitment Portal/test_outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Scoring helpers ────────────────────────────────────────────────────────────
CRITICAL_FIELDS = ['name', 'email', 'phone']
IMPORTANT_FIELDS = ['education', 'experience']
NICE_FIELDS      = ['dob', 'skills', 'publications']

def score_data(d):
    """Return (score 0-100, issues list)."""
    issues = []
    score  = 100

    for f in CRITICAL_FIELDS:
        v = d.get(f)
        empty = not v or (isinstance(v, list) and len(v) == 0) or str(v).strip() == ''
        if empty:
            score -= 15
            issues.append(f'MISSING {f}')

    for f in IMPORTANT_FIELDS:
        v = d.get(f)
        empty = not v or (isinstance(v, list) and len(v) == 0) or str(v).strip() == ''
        if empty:
            score -= 10
            issues.append(f'MISSING {f}')

    for f in NICE_FIELDS:
        v = d.get(f)
        empty = not v or (isinstance(v, list) and len(v) == 0) or str(v).strip() == ''
        if empty:
            score -= 3
            issues.append(f'missing {f}')

    # Penalise obviously bad values
    name = d.get('name', '')
    if name and any(w in str(name).lower() for w in ['candidate', 'unknown', 'none', 'lorem', 'ipsum']):
        score -= 10
        issues.append(f'bad name: {name}')

    email = d.get('email', '')
    if email and ('@' not in str(email) or 'example' in str(email).lower()):
        score -= 5
        issues.append(f'bad email: {email}')

    dob = d.get('dob', '')
    age = d.get('age', '')
    if dob and not age:
        pass  # fine – DOB present, age left to be filled manually
    if age and not dob:
        pass  # fine – age extracted directly

    return max(0, score), issues


def pick_unique_files(all_files, n=55):
    """Pick representative files: prefer unique base-names (no dupes)."""
    seen_bases = {}
    unique = []
    for f in all_files:
        base = os.path.basename(f)
        # strip uid prefix (8 hex chars + underscore)
        stem = base[9:] if len(base) > 9 and base[8] == '_' else base
        if stem not in seen_bases:
            seen_bases[stem] = f
            unique.append(f)
    # Fill up to n if needed
    if len(unique) < n:
        for f in all_files:
            if f not in unique:
                unique.append(f)
            if len(unique) >= n:
                break
    return unique[:n]


# ── Main test loop ─────────────────────────────────────────────────────────────
all_pdfs = sorted(glob.glob(os.path.join(UPLOADS, '*.pdf')))
test_files = pick_unique_files(all_pdfs, n=55)

print(f"Tesseract available: {TESSERACT_AVAILABLE}")
print(f"Total PDFs in uploads: {len(all_pdfs)}")
print(f"Selected for testing : {len(test_files)}")
print("=" * 80)

results = []
pass_count = 0
fail_count = 0
pdf_ok = 0
pdf_fail = 0

for idx, fpath in enumerate(test_files, 1):
    bn = os.path.basename(fpath)
    t0 = time.time()
    result = {
        'idx': idx, 'file': bn, 'type': '?', 'method': '?',
        'name': '', 'email': '', 'phone': '', 'dob': '', 'age': '',
        'edu_count': 0, 'exp_count': 0, 'score': 0, 'issues': [],
        'pdf_ok': False, 'error': None, 'elapsed': 0
    }

    try:
        parsed = parse_file(fpath)
        is_scanned = parsed['is_scanned']
        raw_text   = parsed['raw_text']
        result['type'] = 'SCANNED' if is_scanned else 'DIGITAL'

        # Extract text
        if is_scanned:
            text = extract_text_via_ocr(fpath)
            result['method'] = 'OCR'
        else:
            text = raw_text
            result['method'] = 'DIGITAL'

        if not text or len(text.strip()) < 100:
            result['error'] = 'No usable text extracted'
            fail_count += 1
            results.append(result)
            continue

        # NLP parse
        data = parse_resume_text(text)

        result['name']      = data.get('name', '')
        result['email']     = data.get('email', '')
        result['phone']     = data.get('phone', '')
        result['dob']       = data.get('dob', '')
        result['age']       = data.get('age', '')
        result['edu_count'] = len(data.get('education', []))
        result['exp_count'] = len(data.get('experience', []))

        score, issues = score_data(data)
        result['score']  = score
        result['issues'] = issues

        # PDF generation
        out_pdf = os.path.join(OUTPUT_DIR, f"test_{idx:03d}_{bn}")
        generate_candidate_pdf(data, out_pdf)
        if os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 3000:
            result['pdf_ok'] = True
            pdf_ok += 1
        else:
            result['issues'].append('PDF generation failed or too small')
            pdf_fail += 1

        if score >= 50 and result['pdf_ok']:
            pass_count += 1
        else:
            fail_count += 1

    except Exception as e:
        result['error'] = str(e)
        fail_count += 1
        pdf_fail += 1

    result['elapsed'] = round(time.time() - t0, 1)
    results.append(result)

    # Live progress
    status = '✓' if result['score'] >= 50 and result['pdf_ok'] else '✗'
    print(f"[{idx:02d}/{len(test_files)}] {status} {result['type'][:1]}|{result['method'][:3]} "
          f"score={result['score']:3d} edu={result['edu_count']} exp={result['exp_count']} "
          f"pdf={'OK' if result['pdf_ok'] else 'FAIL'} "
          f"name={repr(result['name'])[:30]} "
          f"t={result['elapsed']}s  {bn[:45]}")
    if result['issues']:
        critical = [i for i in result['issues'] if i.startswith('MISSING')]
        if critical:
            print(f"         ISSUES: {', '.join(critical)}")

# ── Summary ────────────────────────────────────────────────────────────────────
print()
print("=" * 80)
print("COMPREHENSIVE TEST SUMMARY")
print("=" * 80)
total = len(results)
avg_score = sum(r['score'] for r in results) / total if total else 0
scanned_count  = sum(1 for r in results if r['type'] == 'SCANNED')
digital_count  = sum(1 for r in results if r['type'] == 'DIGITAL')

print(f"Total tested  : {total}")
print(f"  Digital PDFs: {digital_count}")
print(f"  Scanned PDFs: {scanned_count}")
print(f"Pass (score≥50 + PDF OK): {pass_count}/{total}  ({100*pass_count//total if total else 0}%)")
print(f"Fail           : {fail_count}/{total}")
print(f"PDF generated  : {pdf_ok}/{total}")
print(f"PDF failed     : {pdf_fail}/{total}")
print(f"Average score  : {avg_score:.1f}/100")
print()

# Worst performers
failures = [r for r in results if r['score'] < 50 or not r['pdf_ok'] or r.get('error')]
if failures:
    print(f"── {len(failures)} Files needing attention ──────────────────────────")
    for r in failures:
        print(f"  [{r['idx']:02d}] score={r['score']} pdf={'OK' if r['pdf_ok'] else 'FAIL'} "
              f"  {r['file']}")
        if r.get('error'):
            print(f"       ERROR: {r['error']}")
        if r['issues']:
            print(f"       Issues: {', '.join(r['issues'][:5])}")
    print()

# Field coverage stats
name_ok   = sum(1 for r in results if r['name'] and 'bad name' not in ' '.join(r['issues']))
email_ok  = sum(1 for r in results if r['email'])
phone_ok  = sum(1 for r in results if r['phone'])
dob_ok    = sum(1 for r in results if r['dob'])
edu_ok    = sum(1 for r in results if r['edu_count'] > 0)
exp_ok    = sum(1 for r in results if r['exp_count'] > 0)

print("── Field Extraction Coverage ──────────────────────────────────────────")
print(f"  Name    : {name_ok}/{total}  ({100*name_ok//total if total else 0}%)")
print(f"  Email   : {email_ok}/{total}  ({100*email_ok//total if total else 0}%)")
print(f"  Phone   : {phone_ok}/{total}  ({100*phone_ok//total if total else 0}%)")
print(f"  DOB     : {dob_ok}/{total}  ({100*dob_ok//total if total else 0}%)")
print(f"  Educ.   : {edu_ok}/{total}  ({100*edu_ok//total if total else 0}%)")
print(f"  Exp.    : {exp_ok}/{total}  ({100*exp_ok//total if total else 0}%)")

# Save JSON report
report_path = os.path.join(OUTPUT_DIR, 'test_report.json')
with open(report_path, 'w', encoding='utf-8') as jf:
    json.dump(results, jf, indent=2, ensure_ascii=False)
print(f"\nFull report saved: {report_path}")
print("Done.")
