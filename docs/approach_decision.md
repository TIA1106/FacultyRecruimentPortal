# Finalized System Approach & Proposed Workflow

This document summarizes the understanding and proposed workflow finalized after completing Week 1 research, feasibility experiments, and initial analysis.

---

# 1. Key Learnings from Week 1

During the initial research phase, the following observations were made:

* Resume structures vary significantly across candidates.
* Digital PDFs and scanned PDFs behave differently during text extraction.
* Academic or research-oriented resumes are more detailed and may contain sections such as publications, teaching experience, certifications, and research work.
* Generic Named Entity Recognition (NER) models may not always detect resume information accurately without additional handling.

These observations helped in understanding the practical challenges involved in resume parsing.


# 2. Reasoning Behind the Approach

### Digital PDFs

Experiments showed that searchable digital PDFs allow direct text extraction and can be processed more easily.

### Scanned PDFs

Scanned or image-based resumes may require OCR before usable text can be extracted.

### Text Cleaning

Formatting inconsistencies such as spacing issues and unusual bullet symbols may require cleaning before information extraction.

### Information Extraction

A combination of regex and NLP-based techniques may help in extracting useful information such as names, education details, experience, and skills.

---

# 3. Conclusion

Based on the research and feasibility experiments conducted during Week 1, a basic implementation approach was proposed to guide future development and experimentation.
