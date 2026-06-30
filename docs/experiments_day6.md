# Feasibility Experiments: OCR and Basic NER

This document contains small feasibility experiments conducted to better understand OCR requirements and basic Named Entity Recognition (NER) behavior for resume parsing.

---

# 1. Experiment 1: OCR Setup Feasibility

### Objective

To understand OCR requirements for scanned resumes.

### Implementation

Explored **pytesseract** and attempted a basic OCR setup.

### Observation

* `pytesseract` depends on the external **Tesseract OCR** software being installed separately.
* Since the OCR engine was not configured yet, complete OCR testing could not be performed.

### Learning

Scanned or image-based resumes may require OCR processing, but proper environment setup is necessary before testing.

---

# 2. Experiment 2: spaCy Named Entity Recognition (NER)

### Objective

To observe how spaCy's pre-trained NER model behaves on resume text.

### Implementation

Ran spaCy's `en_core_web_sm` model on sample resume text extracted from a faculty resume.

### Observations

The following entity detections were observed:

| Extracted Text                         | Detected Label |
| -------------------------------------- | -------------- |
| D.                                     | NORP           |
| Kavitha                                | GPE            |
| Department of Information Technology   | ORG            |
| PVP Siddhartha Institute of Technology | ORG            |
| Andhra Pradesh                         | PERSON         |

Several classifications were incorrect. For example:

* Candidate names were not always detected correctly.
* Locations were sometimes misclassified.
* Institution and department names were identified more reliably.

### Learning

Pre-trained NER models can identify some useful information from resume text, but resume-specific extraction may require additional filtering or customization for better accuracy.

---

# Overall Conclusion

The experiments helped in understanding the feasibility of OCR and NLP-based extraction methods. OCR requires additional setup before testing, and generic NER models may not always work accurately on resume-specific text without further improvements.
