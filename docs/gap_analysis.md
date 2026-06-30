# Gap Analysis & Initial Text Extraction Experiment

This document contains early observations and small experiments conducted to understand challenges involved in resume parsing and text extraction.

---

# 1. Identified Gaps in Resume Parsing

Based on the research and datasets explored during the initial phase, the following practical challenges were identified:

## 1.1 Scanned PDF Challenge

Text extraction libraries such as **PyMuPDF** work effectively for digital PDFs containing selectable text. However, scanned or image-based PDFs may return little or no readable text because the content exists as images rather than machine-readable text.

### Observation

This suggests that scanned resumes may require additional handling for extracting usable text.

---

## 1.2 Resume Structure Variability

Resume formats vary significantly across candidates.

### Common Variations Observed

* Different section ordering
* Different naming conventions for sections
* Multi-column layouts
* Different formatting styles

### Example

A qualification may appear in different forms:

* *PhD*
* *Ph.D.*
* *Doctor of Philosophy*

Such variations may require normalization during information extraction.

---

## 1.3 Academic Resume Complexity

Academic or research-oriented resumes are often longer and more detailed than standard corporate resumes.

### Additional Sections Commonly Found

* Publications
* Research work
* Teaching experience
* Workshops & certifications
* Conference participation

These sections may require more customized extraction compared to standard resumes.

---

## 1.4 Text Formatting Issues

Text extracted from PDFs may contain:

* Unusual bullet symbols
* Extra spacing and blank lines
* Formatting inconsistencies

These issues may affect downstream information extraction.

---

# 2. Small Text Extraction Experiment (PyMuPDF)

A small experiment was conducted using **PyMuPDF** to compare text extraction behavior between digital and scanned PDFs.

### Purpose

To understand how PDF type affects text extraction quality.

### Experiment Summary

#### Digital PDF Result

A **7-page digital faculty resume PDF** was tested. Text extraction worked successfully and approximately **10,842 characters** of readable text were extracted.

**Observations:**

* Readable text was extracted successfully
* Resume sections such as education, experience, and contact details appeared correctly
* Minor formatting inconsistencies such as unusual bullet symbols and spacing issues were observed

#### Scanned PDF Result

A **1-page scanned resume PDF** was tested for comparison.

**Observations:**

* The extraction completed successfully but returned only **2 characters** of text
* No meaningful resume content was extracted
* The document appeared image-based rather than text-based

### Conclusion

The experiment showed a clear difference between digital and scanned PDFs. Digital resumes can be processed effectively through direct text extraction, whereas scanned/image-based resumes may require additional methods for extracting meaningful text. Formatting inconsistencies in extracted text may also require cleaning before information extraction.
