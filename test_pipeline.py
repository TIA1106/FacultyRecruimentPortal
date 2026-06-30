import sys
sys.path.insert(0, 'backend/app')

# Test the full pipeline
from cleaner import clean_text
from nlp_engine import extract_email, parse_resume_text

# Simulate a DOCX text with email in Contact section
test_text = """
John Heartman

Contact
Address
Seattle, WA, 98101
Phone
(555)555-5555
Email
John.Heartman@example.com

Professional Summary
Certified Nursing Assistant with over 10 years of experience in patient care.

Education
2014-05 Master of Science: Healthcare Administration
University of Illinois - Champaign, Illinois
"""

print("=" * 70)
print("TESTING EMAIL EXTRACTION PIPELINE")
print("=" * 70)

print("\n1. Original text (first 300 chars):")
print(repr(test_text[:300]))

print("\n2. After cleaning:")
cleaned = clean_text(test_text)
print(repr(cleaned[:300]))

print("\n3. Email extraction from cleaned text:")
email = extract_email(cleaned)
print(f"Email found: '{email}' " + ("✓ SUCCESS" if email else "✗ FAILED (EMPTY)"))

print("\n4. Full NLP parse:")
parsed = parse_resume_text(cleaned)
print(f"Parsed email field: '{parsed.get('email', 'MISSING')}'")

print("\n" + "=" * 70)
