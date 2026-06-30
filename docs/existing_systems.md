# Study of Existing Recruitment Systems and ATS Technologies

**Course Code:** PS1101 (Practice School I) | **Organization:** JK Lakshmipat University, Jaipur

## 1\. Overview of Existing Recruitment \& Resume Parsing Systems

During domain research, different recruitment platforms and resume parsing approaches were explored to understand how modern hiring systems process candidate information and resumes.



\### LinkedIn Hiring / Recruiter



LinkedIn Recruiter was reviewed at a high level to understand how professional hiring systems work. It mainly focuses on recruiter search, keyword matching, profile-based hiring, and structured candidate information.



\### Workday Recruiter \& Lever



Workday and Lever were identified as commonly used enterprise Applicant Tracking Systems (ATS). However, due to restricted access and enterprise-level onboarding requirements, detailed practical exploration was limited. Publicly available feature descriptions suggested that these platforms focus on recruitment workflow management, candidate tracking, and standard resume screening.



\### Affinda Resume Parser (Practical Exploration)



Affinda was explored practically by testing a sample faculty CV to understand how structured information is extracted automatically from resumes.



The parser successfully extracted:



\* Personal information and contact details

\* Education history

\* Work experience

\* Publications and academic activities

\* Skills and language information



\#### Observations from Affinda Testing



Several limitations were observed while processing long academic resumes:



\* Inconsistencies in date extraction in some sections

\* Difficulty handling publication-heavy and research-oriented content

\* Misclassification of some academic activities and workshops

\* Complex faculty CV structure being harder to process than short corporate resumes



These observations helped identify a practical gap between general resume parsers and the requirements of a faculty-oriented recruitment portal for academic institutions.

## 2\. Concept of Resume Parsing

Conceptually, resume parsing involves converting a semi-structured or unstructured resume document into a structured data format (such as JSON or XML). The process generally consists of:

1. **Document Ingestion:** Reading the source file (PDF or Image).
2. **Text Extraction:** Using layout libraries or Optical Character Recognition (OCR) to convert pages into raw string streams.
3. **Information Extraction:** Analyzing the string streams using Rule-Based Heuristics (regular expressions) or Machine Learning (Named Entity Recognition - NER) to classify specific segments of text (such as names, dates, organizations, and skills).
4. **Data Normalization:** Cleaning extracted strings and mapping them into standardized schema formats.

## 3\. Limitations of Existing Systems for Academic CVs

Existing commercial and open-source parsers exhibit major gaps when applied to faculty recruitment:

* **Ignored Academic Sections:** Standard tools discard lists of research papers, book chapters, patents, and supervised dissertations, treating them as generic body text or noise.
* **Inability to Parse Complex Qualifications:** Corporate parsers struggle to link specific degrees with their corresponding specialization, university, passing year, and CGPA when they are listed across multiple lines or in tabular grids.
* **Rigid Corporate Assumptions:** Existing tools assume a standard 1 or 2-page chronological format. An academic CV is typically 5 to 10 pages long, causing standard parsers to truncate text or lose context.
* **Failure on Scanned Input:** Many corporate portals reject image-only scanned PDFs immediately, which is unacceptable for walk-in drives where resumes are scanned in bulk.

## 4\. Key Takeaways for Our Project

To overcome these barriers, our portal will implement:

* A specialized dual-route parser that automatically routes searchable PDFs to PyMuPDF and scanned PDFs to Tesseract OCR.
* Custom NLP heuristics designed to extract and isolate Ph.D., Master's, and Bachelor's credentials.
* A custom citation parser that identifies years and publishers to structure a complete research publication list.

