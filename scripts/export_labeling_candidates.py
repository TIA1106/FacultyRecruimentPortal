import os
import json
import csv
import re
from pathlib import Path


OUT_DIR = Path(os.getcwd()) / 'outputs'
CONF_DIR = Path(os.getcwd()) / 'outputs_confidence'
OUT_DIR.mkdir(exist_ok=True)


def suspect_reason_for_line(line: str):
    l = line.lower()
    company_inds = ['llp','ltd','pvt','inc','co.','company','associates','associate','group','firm','solutions','technologies','services','consult','advocate','adv','systems','labs','corp','corporation','limited','plc','consulting']
    inst_words = ['university','college','institute','school','academy','department','faculty','institute of','school of law','iit','nit','iim','bits']
    degree_inds = ['ph.d','phd','b.tech','m.tech','b.e','m.e','b.sc','m.sc','b.a','m.a','mba','llb','llm','jd','doctor of']
    has_company = any(ind in l for ind in company_inds)
    has_institution = any(inst in l for inst in inst_words)
    has_degree = any(d in l for d in degree_inds)
    has_year = bool(re.search(r'\b(19|20)\d{2}\b', l))
    has_cgpa = 'cgpa' in l or 'gpa' in l or '%' in l
    if 'intern' in l:
        return 'intern_keyword'
    if has_company and not has_institution and not has_degree:
        return 'company_no_institution'
    if has_year and has_company and not has_degree:
        return 'year_and_company_no_degree'
    if has_cgpa and has_company and not has_degree:
        return 'cgpa_and_company'
    if has_degree and not has_company:
        return 'degree_like'
    return ''


def main():
    files = sorted(CONF_DIR.glob('*.json'))
    out_csv = OUT_DIR / 'labeling_candidates.csv'
    rows = []
    for p in files:
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
            parsed = data.get('parsed', {})
            edu = parsed.get('education', []) or []
            exp = parsed.get('experience', []) or []
            conf = parsed.get('confidence', {}) or {}

            edu_conf = conf.get('education', '')
            exp_conf = conf.get('experience', '')

            for e in edu:
                reason = suspect_reason_for_line(e)
                try:
                    field_conf_val = float(edu_conf) if edu_conf != '' else None
                except Exception:
                    field_conf_val = None
                if reason or (field_conf_val is not None and field_conf_val < 0.6):
                    rows.append({'file': p.name, 'line_text': e, 'current_field': 'education', 'field_conf': edu_conf, 'reason': reason, 'source': str(p)})

            for ex in exp:
                reason = suspect_reason_for_line(ex)
                try:
                    field_conf_val = float(exp_conf) if exp_conf != '' else None
                except Exception:
                    field_conf_val = None
                if reason or (field_conf_val is not None and field_conf_val < 0.6):
                    rows.append({'file': p.name, 'line_text': ex, 'current_field': 'experience', 'field_conf': exp_conf, 'reason': reason, 'source': str(p)})
        except Exception as e:
            print('skipping', p, 'error', e)

    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        fieldnames = ['file','line_text','current_field','field_conf','reason','source','suggested_label']
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({**r, 'suggested_label': ''})

    print('Wrote', out_csv, 'candidates:', len(rows))


if __name__ == '__main__':
    main()
