import unittest
import sys
import os

# Add project root to path so package imports resolve cleanly during test discovery
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.cleaner import clean_text
from backend.app.utils import normalize_extracted_data, FIXED_SCHEMA
from backend.app.nlp_engine import extract_email, extract_phone, extract_skills, extract_publications, parse_resume_text
from backend.app.layout_parser import extract_faculty_form_fields

class TestResumeParserModules(unittest.TestCase):
    
    def test_clean_text(self):
        """Test that cleaner.py correctly cleans and normalizes text."""
        raw_text = "Hello  World!\n\n\n• Point 1\r\n“Smart Quotes”\n\n\n\n"
        expected = "Hello World!\n\n- Point 1\n\"Smart Quotes\""
        self.assertEqual(clean_text(raw_text), expected)
        
    def test_schema_normalization(self):
        """Test that utils.py normalizes data exactly to the fixed schema."""
        raw_data = {
            "name": "Dr. John Doe",
            "email": "john.doe@example.com",
            "skills": ["Python", "Flask", ""], # Empty item should be removed
            "invalid_key": "some_value" # Unrelated keys should be dropped
        }
        normalized = normalize_extracted_data(raw_data)
        
        # Verify schema keys
        self.assertEqual(set(normalized.keys()), set(FIXED_SCHEMA.keys()))
        self.assertEqual(normalized["name"], "Dr. John Doe")
        self.assertEqual(normalized["email"], "john.doe@example.com")
        self.assertEqual(normalized["skills"], ["Python", "Flask"])
        self.assertNotIn("invalid_key", normalized)
        
    def test_email_extraction(self):
        """Test regex extraction of email addresses."""
        text = "Contact me at sarah.connor@jklu.edu.in or personal: sarah@gmail.com"
        email = extract_email(text)
        self.assertEqual(email, "sarah.connor@jklu.edu.in")
        
    def test_phone_extraction(self):
        """Test regex extraction of phone numbers."""
        text1 = "Phone: +91-98765-43210. Email: test@test.com"
        text2 = "Call me at (123) 456-7890"
        self.assertEqual(extract_phone(text1), "+91-98765-43210")
        self.assertEqual(extract_phone(text2), "(123) 456-7890")
        
    def test_skills_extraction(self):
        """Test matching of skills from text."""
        text = "Experienced in Python programming, Machine Learning, and curriculum design. Also knows Docker."
        skills = extract_skills(text)
        self.assertIn("Python", skills)
        self.assertIn("Machine Learning", skills)
        self.assertIn("Curriculum Design", skills)
        self.assertIn("Docker", skills)
        self.assertNotIn("Java", skills) # Not present in text
        
    def test_publications_extraction(self):
        """Test extraction of publications from text containing citations."""
        text = "Publications:\n1. Doe, J., 'AI in Education', IEEE Journal, 2024.\n2. Smith, A., 'Flask Microservices', ACM Vol. 4, pp. 12-15, 2021.\nNext section is Skills."
        pubs = extract_publications(text)
        self.assertEqual(len(pubs), 2)
        self.assertIn("Doe, J., 'AI in Education', IEEE Journal, 2024.", pubs)
        
    def test_full_nlp_pipeline(self):
        """Test that the full parser runner executes and returns valid dictionary."""
        resume_text = """
        Dr. Jane Smith
        jane.smith@jklu.edu.in | +91 99999 88888
        
        EDUCATION
        Ph.D. in Computer Science, IIT Delhi, 2020
        
        SKILLS
        Python, Flask, Teaching, Research, NLP
        
        PUBLICATIONS
        Jane Smith, 'Algorithms for Natural Language Processing', Springer, (2022).
        """
        parsed = parse_resume_text(resume_text)
        normalized = normalize_extracted_data(parsed)
        
        self.assertEqual(normalized["name"], "Jane Smith")
        self.assertEqual(normalized["email"], "jane.smith@jklu.edu.in")
        self.assertEqual(normalized["phone"], "+91 99999 88888")
        self.assertTrue(any("Ph.D." in edu for edu in normalized["education"]))
        self.assertIn("Python", normalized["skills"])
        self.assertIn("Flask", normalized["skills"])
        self.assertTrue(len(normalized["publications"]) > 0)

    def test_resume_layout_from_sample_image(self):
        """Test extraction on the sample Kevin Brown resume layout."""
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
        self.assertEqual(parsed["name"], "Kevin Brown")
        self.assertEqual(parsed["headline"], "Software Engineer")
        self.assertEqual(parsed["location"], "Notre Dame, IN")
        self.assertEqual(parsed["email"], "kevin@hiration.com")
        self.assertEqual(parsed["phone"], "(443) 123 4567")
        self.assertTrue(any("University of Notre Dame" in edu for edu in parsed["education"]))
        self.assertIn("Application Designing", parsed["skills"])
        self.assertIn("Software Testing and Debugging", parsed["skills"])
        self.assertIn("Data Structures and Algorithms", parsed["skills"])
        self.assertTrue(any("Software Engineering Intern" in exp for exp in parsed["experience"]))
        self.assertTrue(any("Student Developer" in exp for exp in parsed["experience"]))

    def test_robust_name_extraction_formats(self):
        """Test fallback extraction for non-standard formats when spaCy load is bypassed or NER misses it."""
        from backend.app.nlp_engine import extract_name
        
        # Test all-caps name
        text1 = "JOHN DOE\nEmail: john@doe.com\n"
        self.assertEqual(extract_name(text1, None), "JOHN DOE")
        
        # Test middle initial and title prefix
        text2 = "Dr. John D. Doe\nPhone: 1234567890\n"
        self.assertEqual(extract_name(text2, None), "Dr. John D. Doe")
        
        # Test name with trailing/leading spacing
        text3 = "   Jane   S.   Smith   \nEmail: jane@smith.com\n"
        self.assertEqual(extract_name(text3, None), "Jane S. Smith")

    def test_ocr_resilient_extraction(self):
        """Test OCR-resilient extraction of name and phone number from scanned text patterns."""
        from backend.app.nlp_engine import extract_name
        
        # Test OCR split name (JACK and FARRELL on separate lines)
        text_name = "JACK\nFARRELL\nWarehouse Worker\n"
        self.assertEqual(extract_name(text_name, None), "JACK FARRELL")
        
        # Test OCR erroneous phone number
        text_phone = "800 Butterfly lane, New York, NY {718) SOS-7112"
        self.assertEqual(extract_phone(text_phone), "(718) 505-7112")

    def test_pdf_generator_parsers(self):
        """Test the improved education and experience entry parsers in pdf_generator."""
        from backend.app.pdf_generator import parse_education_entry, parse_experience_entry
        
        # Test Case 1: Pipe-separated education with CGPA
        edu1 = "B.Tech in Computer Science | JK Lakshmipat University, Jaipur | 2022 | CGPA: 8.5"
        parsed_edu1 = parse_education_entry(edu1)
        self.assertEqual(parsed_edu1["degree"], "B.E. / B.Tech")
        self.assertEqual(parsed_edu1["spec"], "Computer Science")
        self.assertEqual(parsed_edu1["inst"], "JK Lakshmipat University, Jaipur")
        self.assertEqual(parsed_edu1["univ"], "JK Lakshmipat University, Jaipur")
        self.assertEqual(parsed_edu1["year"], "2022")
        self.assertEqual(parsed_edu1["cgpa"], "8.5")
        
        # Test Case 2: Pipe-separated education with percentage
        edu2 = "M.Tech in Information Technology | IIT Delhi | 2014 | Marks: 85%"
        parsed_edu2 = parse_education_entry(edu2)
        self.assertEqual(parsed_edu2["degree"], "M.Tech.")
        self.assertEqual(parsed_edu2["spec"], "Information Technology")
        self.assertEqual(parsed_edu2["inst"], "IIT Delhi")
        self.assertEqual(parsed_edu2["univ"], "IIT Delhi")
        self.assertEqual(parsed_edu2["year"], "2014")
        self.assertEqual(parsed_edu2["percent"], "85")
        
        # Test Case 3: OCR education with comma and no pipe
        edu3 = "Ph.D. Computer Science, IIT Delhi, 2019, CGPA: 9.2"
        parsed_edu3 = parse_education_entry(edu3)
        self.assertEqual(parsed_edu3["degree"], "Ph.D.")
        self.assertEqual(parsed_edu3["inst"], "IIT Delhi")
        self.assertEqual(parsed_edu3["univ"], "IIT Delhi")
        self.assertEqual(parsed_edu3["year"], "2019")
        self.assertEqual(parsed_edu3["cgpa"], "9.2")
        
        # Test Case 4: No placeholders when not found
        edu4 = "Some Generic Degree | 2020"
        parsed_edu4 = parse_education_entry(edu4)
        self.assertEqual(parsed_edu4["inst"], "")
        self.assertEqual(parsed_edu4["univ"], "")
        
        # Test Case 5: Pipe-separated experience with present date
        exp1 = "Assistant Professor | JK Lakshmipat University, Jaipur | July 2021 to Present"
        parsed_exp1 = parse_experience_entry(exp1)
        self.assertEqual(parsed_exp1["desig"], "Assistant Professor")
        self.assertEqual(parsed_exp1["org"], "JK Lakshmipat University, Jaipur")
        self.assertEqual(parsed_exp1["doj"], "July 2021")
        self.assertEqual(parsed_exp1["dol"], "Present")
        self.assertEqual(parsed_exp1["years"], "5") # 2026 - 2021 = 5 years
        
        # Test Case 6: Experience with date range
        exp2 = "Software Engineering Intern | Multi Learn Technologies | Jan 2021 to June 2021"
        parsed_exp2 = parse_experience_entry(exp2)
        self.assertEqual(parsed_exp2["desig"], "Software Engineering Intern")
        self.assertEqual(parsed_exp2["org"], "Multi Learn Technologies")
        self.assertEqual(parsed_exp2["doj"], "Jan 2021")
        self.assertEqual(parsed_exp2["dol"], "June 2021")

    def test_faculty_layout_field_extraction(self):
        """Test layout-aware extraction on the Kavitha faculty application PDF."""
        sample_pdf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'test_kavitha.pdf')
        if not os.path.exists(sample_pdf):
            self.skipTest("sample PDF not present in workspace")

        fields = extract_faculty_form_fields(sample_pdf)
        self.assertEqual(fields["father_name"], "D.Subrahmanyeswara Rao")
        self.assertEqual(fields["husband_name"], "Dr.D.V.S.Chowdary")

if __name__ == '__main__':
    unittest.main()
