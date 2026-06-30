# Fortnightly Report 1
**Project Title:** Faculty Recruitment Portal (AI Resume Parsing System)  
**Duration:** Day 1 to Day 14 (Week 1 & 2)  
**Institution:** JK Lakshmipat University  
**Course Code:** PS1101 (Practice School I)  

---

## 1. Objectives Achieved
During the first fortnight, the primary focus was on establishing the academic context of the Practice School I internship, performing a thorough literature survey, evaluating standard datasets, designing the core system architecture, and setting up the developer workspace.

### 1.1 literature Survey & Domain Research (Days 1 & 2)
* **Objective:** Define the differences between standard corporate resumes and academic CVs and evaluate text extraction strategies.
* **Why:** Academic recruitment requires analyzing distinct candidate markers: detailed educational qualifications (Ph.D., Master's), research publications (journals, conferences, citations), teaching experience, academic pedagogy, and grants secured. Standard parsers often focus purely on corporate metrics, necessitating a specialized parsing pipeline.
* **How:** Surveyed existing text extraction methodologies, contrasting digital text extraction with Optical Character Recognition (OCR). Evaluated NLP models for Named Entity Recognition (NER), specifically spaCy’s pre-trained English models (`en_core_web_sm`).
* **When:** Completed during Days 1 and 2.

### 1.2 Kaggle Dataset Analysis & Profiling (Days 3 & 4)
* **Objective:** Analyze and map standard datasets to guide system schema requirements.
* **Why:** Designing a highly-scalable system requires understanding the standard distribution of candidate attributes.
* **How:** Checked the **Kaggle Structured Resume Dataset** (`people.csv`, `education.csv`, `skills.csv`) and PDF resume datasets across distinct career categories. Map standard database schemas where relational keys link individual candidate records to their educational histories and skill tags.
* **When:** Completed during Days 3 and 4.

### 1.3 System Architecture Block Design & Planning (Days 5 to 7)
* **Objective:** Map system dataflows, draft the Software Requirements Specification (SRS), and present the conceptual plan for supervisor approval.
* **Why:** Planning before implementation guarantees a modular system design and mitigates issues with system dependencies (like Tesseract OCR) on different host operating systems.
* **How:** Developed a block diagram mapping the dual-route parsing flow (digital PDF extraction vs scanned OCR routing). Drafted the SRS defining the technological stack: Python, Flask, spaCy, PyMuPDF, pytesseract, and ReportLab. Completed the week 1 milestone check-in with the Faculty Supervisor.
* **When:** Completed during Days 5, 6, and 7.

### 1.4 Environment Isolation & Workspace Bootstrapping (Days 8 to 11)
* **Objective:** Create the directory structures and construct a reproducible Python environment.
* **Why:** Dependency isolation is essential to prevent system libraries (such as spaCy and PyMuPDF) from conflicting with global packages.
* **How:** Set up the workspace folders (`backend/app`, `logs/`, `docs/`, `tests/`, `scripts/`, `uploads/`, `outputs/`). Initialized a virtual environment (`.venv`), compiled all system packages in `requirements.txt`, and automated the programmatic download of spaCy's language model (`en_core_web_sm`) during app startup.
* **When:** Completed during Days 8, 9, 10, and 11.

### 1.5 Flask API Skeleton Coding (Days 12 to 14)
* **Objective:** Construct the basic Flask endpoints to establish a core routing skeleton.
* **Why:** Building the API endpoints early facilitates continuous integration and testing of the frontend and parser modules.
* **How:** Created the Flask application module `backend/app/main.py` and coded the initial routing handlers in `backend/app/routes.py` with mock returns for `/`, `/upload`, and `/download_pdf`. Transferred and organized the Kaggle CSV and PDF datasets under the local `data/` folder.
* **When:** Completed during Days 12, 13, and 14.

---

## 2. Key Learnings
1. **Schema Variability:** Candidate profiles vary dramatically. A standard resume parser must map different forms of the same information (e.g. "B.Tech", "Bachelor of Technology", "B.E.") into a unified, normalized database schema.
2. **Text Capture Routing:** Searchable (digital) PDFs contain embedded text characters, whereas scanned PDFs contain only raw image arrays. Distinguishing them early determines whether the system uses a light, high-speed text extraction path or a more resource-intensive OCR route that takes noticeably longer.
3. **Environment Management:** Programmatic validation of dependencies (such as checking if spaCy's language package is present on the host and automatically downloading it) prevents runtime application crashes.

---

## 3. Challenges Faced & Solutions
* **Discrepancy in PDF Structures:** Initial difficulties in distinguishing between digital searchable text PDFs and scanned image-based PDFs without attempting OCR on every file.
  * *Solution:* Programmed a lightweight heuristic that inspects PyMuPDF text output and flags very short extracted text as likely image-only, routing such files to OCR. The exact threshold is an implementation detail and can be tuned.
* **Tesseract Binary Availability:** pytesseract is a wrapper around the Tesseract OCR binary. If Tesseract is not present, the wrapper will fail at runtime.
  * *Solution:* Developed an environment check that flips a `TESSERACT_AVAILABLE` flag. If missing, the app uses a graceful simulated OCR fallback for development and testing so the system remains functional without the native binary.

---

## 4. Work Plan for Next Fortnight
* Develop the core NLP text parsing modules (`nlp_engine.py`) using spaCy NER and pragmatic regex heuristics.
* Create the text cleaning utility (`cleaner.py`) to standardize raw documents.
* Build file reader routers inside `parser.py` (supporting PDFs: digital and scanned).
* Program the image-to-text OCR pipeline (`ocr_engine.py`) with pytesseract and higher-resolution PyMuPDF renders where needed.

### Week 1 Daily Plan (Added)
To improve traceability, Week 1 has a day-by-day plan:

- **Day 1:** Project scoping & objectives; create `docs/project_scope.md`.
- **Day 2:** Broad literature search; save `docs/lit_sources.md`.
- **Day 3:** Read & summarize 6–8 key papers; produce `docs/paper_summaries.md`.
- **Day 4:** Datasets inventory & download; update `data/README.md`.
- **Day 5:** Quick extraction experiments on 5 samples; write `docs/experiments_day5.md`.
- **Day 6:** Synthesize findings and choose main/fallback pipelines; write `docs/approach_decision.md`.
- **Day 7:** Compile Week 1 report and update `logs/daily_logbook.md`.

