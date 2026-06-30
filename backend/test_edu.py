import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/Faculty Recruitment Portal')
from backend.app.parser import parse_file
from backend.app.nlp_engine import parse_resume_text
from backend.app.pdf_generator import parse_education_entry

parsed = parse_file('d:/Faculty Recruitment Portal/uploads/ede87e0c_INF010008.pdf')
data = parse_resume_text(parsed['raw_text'])

edu_list = data.get('education', [])
print('=== PARSED EDUCATION ENTRIES ===')
for edu_str in edu_list:
    print('Input:', repr(edu_str))
    pe = parse_education_entry(edu_str)
    print('  degree:', pe['degree'])
    print('  other_degree:', pe['other_degree'])
    print('  spec:', pe['spec'])
    print('  inst:', pe['inst'])
    print('  univ:', pe['univ'])
    print('  year:', pe['year'])
    print('  percent:', pe['percent'])
    print('  division:', pe['division'])
    print()
