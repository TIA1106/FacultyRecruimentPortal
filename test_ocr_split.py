import sys
sys.path.insert(0, 'backend/app')
from nlp_engine import extract_email

# Test the exact OCR output format from the debug
test_text = """Contact

Address
Seattle, WA, 98101

Phone
(555)555-5555

E-mail
John.Heartman@example.
com

Skills

Patient Care

Medical Documentation
Vital Signs Monitoring"""

print("=" * 70)
print("TESTING OCR-SPLIT EMAIL EXTRACTION")
print("=" * 70)

result = extract_email(test_text)

print(f"\nExtracted email: '{result}'")

# Check if it's actually the correct email
expected = "john.heartman@example.com"
if result.lower() == expected:
    print(f"✓ PERFECT MATCH - Email correctly extracted!")
elif "john.heartman@example.com" in result.lower():
    print(f"✓ SUCCESS - Email found in result: '{result}'")
elif "john" in result.lower() and "heartman" in result.lower() and "example.com" in result.lower():
    print(f"⚠ PARTIAL - Email components found: '{result}'")
else:
    print(f"✗ FAILED - Expected '{expected}' but got '{result}'")

