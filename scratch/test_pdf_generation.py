import os
import sys

# Ensure backend/app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/app")))

from utils import FIXED_SCHEMA
from pdf_generator import generate_candidate_pdf

# Let's create a realistic mock profile using our newly expanded schema
candidate_data = FIXED_SCHEMA.copy()
candidate_data.update({
    "name": "Dr. Rajesh Kumar Sharma",
    "email": "rajesh.sharma@jklu.edu.in",
    "phone": "+91-9876543210",
    "headline": "Associate Professor in Computer Science",
    "location": "Jaipur, Rajasthan",
    "nationality": "Indian",
    "dob": "15/08/1988",
    "age": "37",
    "father_name": "Shri M. R. Sharma",
    "mother_name": "Smt. Shanti Devi",
    "category": "General",
    "religion": "Hinduism",
    "education": [
        "Ph.D. in Computer Science, JK Lakshmipat University, 2021, CGPA: 9.5",
        "M.Tech. in Information Technology, IIT Delhi, 2014, Marks: 85%",
        "B.E. in Computer Engineering, MNIT Jaipur, 2012, CGPA: 8.2"
    ],
    "skills": ["Machine Learning", "Python", "Data Structures", "Natural Language Processing", "C++"],
    "experience": [
        "Assistant Professor at JK Lakshmipat University, Jaipur (July 2021 to Present)",
        "Assistant Professor at Amity University, Noida (July 2018 to June 2021)",
        "Software Engineer at Infosys Limited, Pune (June 2014 to June 2018)"
    ],
    "publications": [
        "A Hybrid OCR and NLP Pipeline for Academic Resume Parsing, IEEE Transactions on Education, 2024",
        "Deep Learning for Document Image Layout Understanding, Springer Journal of Computer Science, 2022"
    ],
    "thesis_info": [
        {
            "degree": "Ph.D.",
            "title": "Intelligent Resume Classification using Deep NLP and Layout Models",
            "guide": "Dr. K. K. Verma",
            "university": "JK Lakshmipat University"
        },
        {
            "degree": "PG",
            "title": "Optimizing OCR Quality for Devanagari Script Documents",
            "guide": "Prof. S. R. Prasad",
            "university": "IIT Delhi"
        }
    ]
})

output_pdf = "outputs/test_new_format.pdf"
print(f"Generating test PDF at: {output_pdf} ...")
try:
    generate_candidate_pdf(candidate_data, output_pdf)
    print("Success! PDF report generated successfully.")
except Exception as e:
    print(f"Failed to generate PDF: {e}")
