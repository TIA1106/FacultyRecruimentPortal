import spacy

# Load English model
nlp = spacy.load("en_core_web_sm")

# Sample resume text
text = """
D. Kavitha
Senior Assistant Professor
Department of Information Technology
PVP Siddhartha Institute of Technology
Vijayawada, Andhra Pradesh
Email: kavitha_donepudi@yahoo.com
"""

# Process text
doc = nlp(text)

print("Detected Entities:\n")

for ent in doc.ents:
    print(f"Text: {ent.text}")
    print(f"Label: {ent.label_}")
    print("-" * 30)