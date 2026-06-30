import sys
import re
sys.path.insert(0, 'backend/app')

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

Patient Care"""

print("=" * 70)
print("DEBUGGING EMAIL EXTRACTION")
print("=" * 70)

# Test FALLBACK 3 logic directly
print("\n[Testing FALLBACK 3 - Email label search]")
lines_original = test_text.split('\n')
for i, line in enumerate(lines_original):
    line_lower = line.lower().strip()
    print(f"Line {i}: {repr(line_lower[:40])}")
    
    if any(label in line_lower for label in ['email', 'e-mail', 'e.mail']):
        print(f"  ✓ Found email label at line {i}")
        
        # Search this line and next 3 lines for email parts
        search_text = " ".join([lines_original[j].strip() for j in range(i, min(i + 4, len(lines_original)))])
        print(f"  Search text: {repr(search_text)}")
        
        # Try the OCR split pattern
        ocr_split_pattern = r"([A-Za-z0-9._%+-]+)\s*@\s*([A-Za-z0-9.-]+)\s*\.\s*([A-Za-z]{2,})"
        ocr_match = re.search(ocr_split_pattern, search_text)
        
        if ocr_match:
            found_email = f"{ocr_match.group(1)}@{ocr_match.group(2)}.{ocr_match.group(3)}"
            print(f"  ✓ PATTERN MATCHED!")
            print(f"  Groups: {ocr_match.groups()}")
            print(f"  Email: {found_email}")
        else:
            print(f"  ✗ Pattern didn't match")

