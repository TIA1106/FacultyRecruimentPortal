import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from backend.app.nlp_engine import extract_location
from backend.app.nlp_engine import parse_resume_text

sample_text = """
Kevin Brown
Software Engineer
(443) 123 4567 • kevin@hiration.com • Notre Dame, IN • www.linkedin.com/in/kevin
SUMMARY
Tech-savvy software professional possessing experience in designing & implementing software solutions by deploying various programming languages.
KEY SKILLS
• Application Designing • Software Testing and Debugging • Data Structures and Algorithms
• Software Development Life Cycle • Technical Documentation • Report Generation
Technical Skills: Java, JavaScript, C++, HTML5, MySQL, MongoDB
EDUCATION
Bachelor of Computer Science | Minor in Engineering Corporate Practice
University of Notre Dame
Study Abroad Spring Program
Dublin City University
EXPERIENCE
Software Engineering Intern
Multi Learn Technologies
Application Maintenance & Testing
• Gained hands-on experience in developing internal web applications
• Awarded as the "Best Intern of the Month" for above & beyond performance | Jan 2021
Student Developer
Notre Dame Computer Club
• Collaborated with a team of 5 to develop a weather forecasting application by deploying HTML
VOLUNTEER EXPERIENCE
Volunteer
Big Brothers/Big Sisters of Notre Dame and St. Mary's
• Collaborated with 5 volunteers to teach English & Mathematics to a class of ~30 children-at-risk
"""

parsed = parse_resume_text(sample_text)
print('Parsed location:', repr(parsed.get('location')))
print('Parsed name:', parsed.get('name'))
from backend.app.nlp_engine import extract_location
print('Direct extract_location:', repr(extract_location(sample_text)))
# Reproduce the internal _reassemble_contact_text transformation
import re
out_lines = []
for line in sample_text.splitlines():
	toks = line.split()
	if not toks:
		out_lines.append(line)
		continue
	single_frac = sum(1 for t in toks if len(t) == 1) / len(toks)
	digit_frac = sum(1 for t in toks if all(ch.isdigit() for ch in t)) / len(toks)
	if single_frac >= 0.6 or digit_frac >= 0.6:
		line2 = ''.join(toks)
	else:
		line2 = line
	line2 = re.sub(r"([A-Za-z0-9])\s*[\.\,]\s*([A-Za-z0-9])", r"\1.\2", line2)
	line2 = re.sub(r"\s*@\s*", "@", line2)
	out_lines.append(line2)
trans = '\n'.join(out_lines)
print('Transformed sample (first 3 lines):')
print('\n'.join(trans.splitlines()[:6]))
print('Location after transform:', repr(extract_location(trans)))
