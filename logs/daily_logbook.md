# PS-I Daily Logbook
**Project Title:** Faculty Recruitment Portal (AI Resume Parsing System)
**Organization:** JK Lakshmipat University, Jaipur
**Course Code:** PS1101 (Practice School I)
**Student:** [Your Name] | [Roll Number]

---

## Screenshot Instructions
Save screenshots under `logs/screenshots/` using this naming format: `day-[number]-[feature].png`

Suggested captures:
1. Directory structure after workspace setup
2. Flask server running in terminal
3. Frontend home page in browser
4. File upload and parsed result cards
5. Generated PDF report download

---

## Week 1: Understanding the Problem, Research & Planning (Days 1–7)

### Date: 2026-05-25
**Day Number:** Day 1
**Objective:** Understand what the project is about and why it is needed.
**Work Done:** Met with supervisor and discussed the project brief for the Faculty Recruitment Portal. Understood the problem: JKLU HR manually reads each faculty application resume, which takes a lot of time. The goal of this project is to automate that process using Python. Noted down what information needs to be extracted from academic CVs — name, contact, education, publications, teaching experience, skills. Understood how faculty CVs are different from a normal corporate resume (longer, more detailed, includes research papers and conferences).
**Tools Used:** MS Word (notes), Web Browser.
**Output:** Notes document — `docs/project_scope.md`.
**Issues Faced:** None on Day 1.
**Next Step:** Research what tools and systems already exist for resume parsing.

---

### Date: 2026-05-26
**Day Number:** Day 2
**Objective:** Study existing recruitment portals and resume screening systems.
**Work Done:** Browsed and studied how existing platforms handle resume screening — looked at LinkedIn Hiring, Workday, and Lever briefly to understand what automated parsing looks like from a user side. Also went through a few articles on resume parsing in the HR tech space. Noted that most standard parsers are built for corporate resumes and don't handle academic CVs well (no publication section, no teaching history). This confirmed the gap this project is trying to fill.
**Tools Used:** Web Browser, Google.
**Output:** Comparison notes — `docs/existing_systems.md`.
**Issues Faced:** Found it hard to understand the exact parsing logic behind commercial tools since they don't publish their internals. Focused on understanding their input/output behavior instead.
**Next Step:** Read research papers on OCR, NLP, and resume parsing approaches.

---

### Date: 2026-05-27
**Day Number:** Day 3
**Objective:** Read and understand key research papers and technical resources on resume parsing.
**Work Done:** Read through a few papers and documentation sources to understand how automated resume parsing systems work at a technical level:
- "An Overview of the Tesseract OCR Engine" (Smith, 2007) — understood what OCR does and why scanned PDFs need it.
- spaCy documentation for Named Entity Recognition (NER) — understood how NER identifies names, organizations, etc. in text.
- Skimmed LayoutLM paper conceptually — understood the idea of layout-aware extraction (didn't go into implementation details, just the concept).
- Read a few resume parsing blogs and articles for practical understanding.

Did not implement anything today. Focused on understanding what approaches are available.
**Tools Used:** Google Scholar, arXiv, spaCy docs.
**Output:** Paper notes saved in `docs/paper_summaries.md`.
**Issues Faced:** Some papers were heavy to read. Focused on abstracts, conclusions, and practical takeaways rather than full mathematical detail.
**Next Step:** Look at actual resume datasets to understand the data we'll be working with.

---

### Date: 2026-05-28
**Day Number:** Day 4
**Objective:** Study resume datasets available on Kaggle and understand resume formats.
**Work Done:** Found two useful Kaggle datasets:
1. Structured Resume Dataset (`people.csv`, `education.csv`, `skills.csv`) — a relational dataset with thousands of candidate records. Understood that `person_id` links records across tables.
2. PDF Resume Dataset — a collection of PDF resumes organized by category (Data Science, Java Developer, HR, etc.).

Also noted the difference between a standard corporate resume and an academic faculty CV — faculty CVs are longer, include research publications, conference papers, and teaching history.
**Tools Used:** Kaggle, Web Browser.
**Output:** Dataset notes — `data/README.md`.
**Issues Faced:** The Kaggle CSVs are large (120MB+). Didn't download everything yet, just browsed online.
**Next Step:** Do a gap analysis — figure out what current systems can't handle for faculty hiring.

---

### Date: 2026-05-29
**Day Number:** Day 5
**Objective:** Identify gaps and problems in current resume parsing approaches for faculty recruitment.
**Work Done:** Based on what I read in Days 2–4, I listed the main problems:
- Most parsers don't have a publications section.
- Scanned PDFs (common in walk-in drives and legacy HR files) completely fail with text-based parsers.
- Faculty CVs use inconsistent formatting — some list education at the top, some at the bottom.
- Degree abbreviations vary widely (Ph.D., PhD, Doctor of Philosophy — all mean the same thing).
- A parser built for corporate resumes would miss or misclassify a lot of faculty-specific content.

Also did a few small experiments in Python — tried extracting text from a sample PDF using PyMuPDF. Got some output. Noticed that a scanned PDF returned almost no text at all, which confirmed the need for OCR.
**Tools Used:** Python, PyMuPDF, Web Browser.
**Output:** Gap analysis notes — `docs/gap_analysis.md`. Small test script saved locally.
**Issues Faced:** One PDF I tried had encoding issues and returned garbled characters. Noted this as something to handle in the cleaner module later.
**Next Step:** Run more small experiments with spaCy and OCR to explore the approach.

---

### Date: 2026-05-30
**Day Number:** Day 6
**Objective:** Run small feasibility experiments — try text extraction, OCR, and spaCy basics.
**Work Done:** Added a layout-aware faculty form helper in `backend/app/layout_parser.py` that reads the cleaned page text and maps labels to nearby values in the personal details table. Merged those layout hints into `backend/app/routes.py` so father name and husband name can be recovered when the NLP pass leaves a blank or placeholder value. Refined the helper to handle small-text rows where the value appears on the next line or is followed by an adjacent `OCCUPATION` cell. Verified the fix on `outputs/test_kavitha.pdf`, where the father name is extracted as `D.Subrahmanyeswara Rao` and the husband name as `Dr.D.V.S.Chowdary`.
1. Loaded a digital PDF using PyMuPDF and printed extracted text — worked fine.
2. Loaded a scanned PDF — almost no text came out, confirming OCR is needed.
**Issues Faced:** The first extraction attempt used fragmented word-level layout text and did not preserve the table row cleanly. Switching to `pdfplumber` plain page text resolved it, then a second refinement was needed to trim trailing `OCCUPATION` text from the same row.

These experiments helped confirm the overall approach: digital PDFs → PyMuPDF text extraction, scanned PDFs → Tesseract OCR, then spaCy + regex for information extraction.
**Tools Used:** Python, PyMuPDF, spaCy, pytesseract.
**Output:** Short experiment notes — `docs/experiments_day6.md`.
**Issues Faced:** Tesseract was not installed on my system. Noted that a fallback mechanism will be needed for environments without Tesseract.
**Next Step:** Finalize the approach and discuss with supervisor.

---

### Date: 2026-05-31
**Day Number:** Day 7
**Objective:** Finalize the project approach and present Week 1 findings to supervisor.
**Work Done:** Compiled Week 1 findings into a short document — what I researched, what gaps I found, what approach I've decided on. Prepared a simple block diagram showing the overall workflow: upload → detect file type → digital or scanned route → text cleaning → NLP extraction → JSON output → PDF report.

Presented this to the supervisor over email/Zoom. Got approval to move forward with the planned approach starting Week 2.
**Tools Used:** Draw.io, MS Word, email.
**Output:** Supervisor-approved approach document and basic flow diagram — `docs/approach_decision.md`.
**Issues Faced:** None.
**Next Step:** Set up the development environment and workspace folders.

---

## Week 2: Environment Setup, Flask Skeleton & Dataset Organization (Days 8–14)

### Date: 2026-06-01
**Day Number:** Day 8
**Objective:** Set up project workspace structure and write `requirements.txt`.
**Work Done:** Created the project folder at `d:\Faculty Recruitment Portal`. Set up subfolders: `backend/app/`, `logs/`, `docs/`, `tests/`, `scripts/`, `uploads/`, `outputs/`, `data/`. Wrote `requirements.txt` listing all planned packages: flask, spacy, pymupdf, pytesseract, pdfplumber, reportlab.
**Tools Used:** VS Code, PowerShell.
**Output:** Workspace folder structure and requirements file.
**Issues Faced:** None.
**Next Step:** Install dependencies.
**Screenshot to take:** Directory structure in file explorer.
**File naming:** `day-08-directory-structure.png`

---

### Date: 2026-06-02
**Day Number:** Day 9
**Objective:** Install Python dependencies and verify the environment.
**Work Done:** Ran `pip install -r requirements.txt` in PowerShell. Verified Python version. All major packages installed successfully.
**Tools Used:** pip, PowerShell.
**Output:** Installed packages confirmed.
**Issues Faced:** The system didn't recognize `python` command directly — had to use `py` launcher instead. Adjusted all run commands going forward.
**Next Step:** Create Flask app entry point.
**Screenshot to take:** Successful pip install output.
**File naming:** `day-09-pip-install.png`

---

### Date: 2026-06-03
**Day Number:** Day 10
**Objective:** Write `main.py` and basic app initialization.
**Work Done:** Created `backend/app/main.py`. Added code to create required directories if they don't exist on startup. Also added logic to auto-download spaCy's `en_core_web_sm` model programmatically if it's not already present — useful so the app doesn't crash on a fresh machine.
**Tools Used:** Python, VS Code.
**Output:** `main.py` entry point.
**Issues Faced:** Downloading the spaCy model programmatically required wrapping the subprocess call in a try-except. Handled that.
**Next Step:** Write utility helper functions.

---

### Date: 2026-06-04
**Day Number:** Day 11
**Objective:** Write `utils.py` with schema definitions and file helpers.
**Work Done:** Created `backend/app/utils.py`. Added functions to validate file extensions, generate unique filenames using UUID prefixes to avoid overwriting, and defined the standard output schema dictionary (name, email, phone, education, skills, experience, publications).
**Tools Used:** Python.
**Output:** `utils.py` helper module.
**Issues Faced:** Deciding on the schema structure took some time — had to think about what fields are needed for faculty evaluation specifically.
**Next Step:** Create Flask route handlers.

---

### Date: 2026-06-05
**Day Number:** Day 12
**Objective:** Write `routes.py` with Flask endpoint structure.
**Work Done:** Created `backend/app/routes.py`. Defined three routes: `/` (home page), `/upload` (receives file and returns parsed JSON), `/download_pdf` (streams the generated PDF). Used mock return values for now since the actual parser isn't built yet.
**Tools Used:** Python, Flask.
**Output:** Basic routes structure with placeholder responses.
**Issues Faced:** Got relative import errors. Switched to absolute imports which fixed it.
**Next Step:** Download and organize Kaggle datasets.

---

### Date: 2026-06-06
**Day Number:** Day 13
**Objective:** Download and organize the Kaggle structured CSV dataset.
**Work Done:** Downloaded the Kaggle Structured Resume Dataset. Extracted `01_people.csv`, `03_education.csv`, `skills.csv` etc. into `data/resume-dataset-structured/`. Browsed the files to confirm the relational structure — `person_id` links people to their education and skill records.
**Tools Used:** File Explorer, Chrome, Kaggle.
**Output:** Structured CSV files organized under `data/`.
**Issues Faced:** The combined CSV files are about 120MB. Loading them all at once would be slow — noted to use chunked loading later.
**Next Step:** Download PDF resume dataset.

---

### Date: 2026-06-07
**Day Number:** Day 14
**Objective:** Download and organize the Kaggle PDF resume dataset.
**Work Done:** Downloaded and extracted the PDF resume dataset. Organized into domain subfolders under `data/resume-data-pdf/` (Data Science, Java Developer, HR, Accountant, etc.). Browsed a few PDFs manually to understand their formatting — some are clean digital text, a few appear to be scanned.
**Tools Used:** ZIP extractor, File Explorer.
**Output:** PDF resume folders organized under `data/`.
**Issues Faced:** The download was slow due to file size. Extraction took a few minutes but completed without errors.
**Next Step:** Start building the text cleaning module.
**Screenshot to take:** Data folder structure.
**File naming:** `day-14-dataset-folders.png`

---

## Week 3: Text Cleaner, PDF Parser & NLP Engine (Days 15–21)

### Date: 2026-06-08
**Day Number:** Day 15
**Objective:** Build the text cleaner module.
**Work Done:** Created `backend/app/cleaner.py`. Added unicode normalization using `unicodedata.normalize('NFKC', text)` to fix encoding issues. Added regex-based replacements to convert fancy bullet symbols to hyphens, fix smart quotes, remove non-printable characters, and collapse multiple blank lines into one. Tested it on a few raw text samples extracted from PDFs.
**Tools Used:** Python, Regex.
**Output:** `cleaner.py` text normalization module.
**Issues Faced:** Smart quote characters (like `"` and `"`) caused encoding issues when I first tried. NFKC normalization resolved them.
**Next Step:** Build the PDF routing and parsing module.

---

### Date: 2026-06-09
**Day Number:** Day 16
**Objective:** Build `parser.py` to detect and route PDF files.
**Work Done:** Created `backend/app/parser.py`. Used PyMuPDF (`fitz`) to open a PDF and count the total characters extracted. If the character count is below 50, the file is treated as a scanned PDF and sent to the OCR path. If above 50, it goes through the normal digital text extraction path. This simple threshold worked well on the test PDFs I tried.
**Tools Used:** PyMuPDF, Python.
**Output:** `parser.py` with PDF routing logic.
**Issues Faced:** Some digital PDFs had very short metadata text at the top and were almost getting flagged as scanned. The threshold of 50 characters handled this edge case.
**Next Step:** Test the router on more samples and begin planning the NLP engine.

---

### Date: 2026-06-10
**Day Number:** Day 17
**Objective:** Test the PDF router on more samples and start the NLP engine planning.
**Work Done:** Tested `parser.py` against several more PDF samples from the Kaggle dataset — both clean digital and scanned files. Confirmed the character-count threshold is working reliably. Also started sketching out the extraction functions needed in `nlp_engine.py`: email, phone, name, education, skills, experience, publications.
**Tools Used:** PyMuPDF, Python.
**Output:** Tested PDF router, notes on NLP module structure.
**Issues Faced:** A few PDFs had multi-column layouts where PyMuPDF extracted text in a jumbled order. Noted as a known limitation — section parsing will need to be tolerant of this.
**Next Step:** Start building the NLP extraction engine.

---

### Date: 2026-06-11
**Day Number:** Day 18
**Objective:** Write email and phone extractors in `nlp_engine.py`.
**Work Done:** Created `backend/app/nlp_engine.py`. Wrote regex patterns for email extraction and phone number extraction. Phone regex handles common formats including country code (`+91`), brackets, hyphens, and spaces. Configured to return only the first valid match to avoid picking up multiple numbers.
**Tools Used:** Python, Regex.
**Output:** `extract_email()` and `extract_phone()` functions.
**Issues Faced:** Some resumes had two phone numbers listed. Returning only the first one seemed like the safest approach for now.
**Next Step:** Add spaCy-based name extraction.

---

### Date: 2026-06-12
**Day Number:** Day 19
**Objective:** Build the name extraction function using spaCy NER.
**Work Done:** Added `extract_name()` to `nlp_engine.py`. The function first checks the first 3–5 lines of the resume text for a spaCy `PERSON` entity. If that fails, it falls back to a capitalized-word regex. Added a block-word list to skip terms like "Resume", "Curriculum Vitae", "University" that spaCy sometimes incorrectly tags as person names.
**Tools Used:** spaCy, Python.
**Output:** `extract_name()` function with NER + fallback.
**Issues Faced:** spaCy tagged "Curriculum Vitae" as a person entity on a few test cases. The block-word filter fixed this.
**Next Step:** Build the education section parser.

---

### Date: 2026-06-13
**Day Number:** Day 20
**Objective:** Write the education extraction logic.
**Work Done:** Added `extract_education()` to `nlp_engine.py`. It looks for common degree keywords (Ph.D., M.Tech, B.Tech, MBA, etc.) and captures the surrounding lines including institution name and graduation year. Had to handle cases where the degree and year were on separate lines.
**Tools Used:** Python, Regex.
**Output:** `extract_education()` function.
**Issues Faced:** Degree abbreviations are very inconsistent across resumes. Built a list of common variations to match against.
**Next Step:** Build skills and experience extractors.

---

### Date: 2026-06-14
**Day Number:** Day 21
**Objective:** Write skills and experience extractors.
**Work Done:** Added `extract_skills()` — uses a manually curated dictionary of academic and technical skills and does case-insensitive boundary matching against the resume text. Added `extract_experience()` — looks for heading keywords like "Experience", "Work History", "Professional Background" and extracts the lines that follow until the next section heading.
**Tools Used:** Python, Regex.
**Output:** `extract_skills()` and `extract_experience()` functions.
**Issues Faced:** Short skill names like "Go" (the programming language) were matching common English words. Added `\b` word boundary markers to fix this.
**Next Step:** Write the publications parser and start OCR module.

---

## Week 4: Publications Parser, OCR Engine & Fallback (Days 22–28)

### Date: 2026-06-15
**Day Number:** Day 22
**Objective:** Write the academic publications parser.
**Work Done:** Added `extract_publications()` to `nlp_engine.py`. Looks for section headings like "Publications", "Research Papers", "Conference Papers" and extracts lines that look like citations — identified by parenthesized years (2005–2024), publisher terms like IEEE, ACM, Springer, and volume/page indicators.
**Tools Used:** Python, Regex.
**Output:** `extract_publications()` function.
**Issues Faced:** Citation formats vary a lot (APA, IEEE, MLA). Used year patterns and publisher keywords as a general indicator rather than strict format matching.
**Next Step:** Start building the OCR engine.

---

### Date: 2026-06-16
**Day Number:** Day 23
**Objective:** Build the OCR engine module and check for Tesseract.
**Work Done:** Created `backend/app/ocr_engine.py`. Added a check for whether the Tesseract binary is installed on the system. If found, sets `TESSERACT_AVAILABLE = True`. If not, sets it to `False` so the app knows to use a fallback instead of crashing.
**Tools Used:** pytesseract, Python.
**Output:** `ocr_engine.py` with Tesseract availability detection.
**Issues Faced:** Tesseract was not installed on my development machine. This is what motivated building the fallback mechanism.
**Next Step:** Add the PyMuPDF page rendering pipeline.

---

### Date: 2026-06-17
**Day Number:** Day 24
**Objective:** Write the page-to-image conversion for OCR.
**Work Done:** Added page rendering logic to `ocr_engine.py`. Uses PyMuPDF to open each page of a scanned PDF and render it to a high-resolution image using a scaling factor of 2.0 (which roughly doubles the DPI from default 72 to around 144). This higher resolution gives Tesseract better quality input and improves OCR accuracy.
**Tools Used:** PyMuPDF, Pillow.
**Output:** Page rendering function producing PIL images from PDF pages.
**Issues Faced:** At the default rendering resolution, Tesseract was producing poor output on small fonts. Increasing the scaling factor noticeably improved the results.
**Next Step:** Integrate pytesseract for text extraction.

---

### Date: 2026-06-18
**Day Number:** Day 25
**Objective:** Add pytesseract OCR and loop through all pages.
**Work Done:** Added the main OCR loop to `ocr_engine.py`. Converts each PDF page to a PIL image and passes it to `pytesseract.image_to_string()`. Concatenates text from all pages and returns the full result.
**Tools Used:** pytesseract, Pillow.
**Output:** Full scanned PDF text extraction pipeline.
**Issues Faced:** When Tesseract binary is absent, `pytesseract` throws an exception. Wrapped the call in a try-except so the app handles this cleanly.
**Next Step:** Build the OCR mock fallback for testing without Tesseract.

---

### Date: 2026-06-19
**Day Number:** Day 26
**Objective:** Write the OCR fallback function for environments without Tesseract.
**Work Done:** Added `get_ocr_fallback_text()` to `ocr_engine.py`. When Tesseract is unavailable and a scanned PDF is uploaded, instead of crashing or returning empty output, the system returns a realistic sample academic CV text (with a dummy name, Ph.D. qualification, teaching history, and publication). This lets the rest of the pipeline run and be tested without needing Tesseract installed locally.
**Tools Used:** Python.
**Output:** OCR fallback function for development/testing use.
**Issues Faced:** Deciding how realistic the fallback text should be. Settled on a simple but realistic academic profile to make testing meaningful.
**Next Step:** Verify OCR path end-to-end.

---

### Date: 2026-06-20
**Day Number:** Day 27
**Objective:** Test the OCR pipeline on a sample scanned PDF.
**Work Done:** Tested `routes.py` with a sample scanned PDF. Verified that: (1) the parser correctly detects it as scanned (character count below threshold), (2) the OCR engine checks for Tesseract, (3) since Tesseract is absent on my machine, the fallback activates cleanly, and (4) the returned profile goes through the NLP engine and produces structured output. The whole path worked without any crashes.
**Tools Used:** Python, Flask.
**Output:** Confirmed OCR fallback path works end-to-end.
**Issues Faced:** None on this day.
**Next Step:** Start building the PDF report generator.
**Screenshot to take:** Terminal showing OCR fallback message in logs.
**File naming:** `day-27-ocr-fallback-logs.png`

---

### Date: 2026-06-21
**Day Number:** Day 28
**Objective:** Clean up OCR module and add memory management.
**Work Done:** Added explicit memory cleanup inside the OCR page loop — after processing each page, deleted the pixmap object (`del pix`) and called `gc.collect()` to release memory. This prevents memory buildup when processing multi-page scanned documents.
**Tools Used:** Python, gc module.
**Output:** Improved OCR engine with memory cleanup.
**Issues Faced:** During testing with a longer scanned PDF, memory usage climbed. The explicit cleanup fixed this.
**Next Step:** Build the PDF generator module.

---

## Week 5: PDF Generator, Frontend UI & JavaScript (Days 29–35)

### Date: 2026-06-22
**Day Number:** Day 29
**Objective:** Set up `pdf_generator.py` skeleton with ReportLab.
**Work Done:** Created `backend/app/pdf_generator.py`. Set up a `SimpleDocTemplate` with 0.75-inch margins and defined basic paragraph styles using `ParagraphStyle` (title, heading, body). Learned how ReportLab's flowable-based layout works.
**Tools Used:** ReportLab.
**Output:** PDF generator skeleton.
**Issues Faced:** ReportLab's API is different from what I expected — it uses flowables (objects added to a list) rather than direct drawing calls. Took a bit of reading to understand.
**Next Step:** Add pagination — "Page X of Y" footer on every page.

---

### Date: 2026-06-23
**Day Number:** Day 30
**Objective:** Implement `NumberedCanvas` for page numbering.
**Work Done:** Created a `NumberedCanvas` class that extends ReportLab's default canvas. Overrode `showPage()` to save page state and `save()` to count total pages, then loop back and draw "Page X of Y" footer and a header line on each page. This requires a two-pass approach — the first pass saves all pages, the second pass decorates them.
**Tools Used:** ReportLab Canvas.
**Output:** Canvas with working page numbers.
**Issues Faced:** The default ReportLab canvas doesn't know the total page count while drawing early pages. The two-pass approach is the standard workaround.
**Next Step:** Add tables and structured content to the PDF.

---

### Date: 2026-06-24
**Day Number:** Day 31
**Objective:** Add structured sections (Education, Skills, Experience, Publications) to the PDF.
**Work Done:** Added styled tables and list sections to the PDF generator for each extracted field. Wrapped cell content in `Paragraph` objects to handle text wrapping within table cells properly.
**Tools Used:** ReportLab Table, ParagraphStyle.
**Output:** PDF generator that produces a complete candidate summary report.
**Issues Faced:** Text was overflowing out of table cells. Wrapping content in `Paragraph` objects fixed the overflow.
**Next Step:** Build the HTML frontend.

---

### Date: 2026-06-25
**Day Number:** Day 32
**Objective:** Build the HTML frontend template.
**Work Done:** Created `backend/app/templates/index.html`. Added a drag-and-drop file upload zone, a results section that shows parsed fields in cards, and a raw JSON viewer. Used a clean layout with a navy and teal color scheme appropriate for an academic portal.
**Tools Used:** HTML5, CSS.
**Output:** `index.html` template.
**Issues Faced:** Getting the drag-and-drop zone to look right in the layout took some adjustments.
**Next Step:** Write the CSS stylesheet.

---

### Date: 2026-06-26
**Day Number:** Day 33
**Objective:** Write the CSS stylesheet for the UI.
**Work Done:** Created `backend/app/static/css/style.css`. Defined the color palette (Academic Navy `#1E3A8A`, Teal `#0D9488`), font styles, card layouts, and loader animations. Added responsive media queries for smaller screen sizes.
**Tools Used:** CSS3.
**Output:** Styled web application.
**Issues Faced:** The JSON code viewer alignment was off. Used flexbox to fix it.
**Next Step:** Write JavaScript for upload and interaction logic.

---

### Date: 2026-06-27
**Day Number:** Day 34
**Objective:** Write `main.js` for client-side interaction.
**Work Done:** Created `backend/app/static/js/main.js`. Added drag-and-drop detection (with `preventDefault()` on drag events to stop the browser from opening files), file extension validation before upload, and an AJAX `fetch()` call to POST the file to the `/upload` endpoint. Added DOM update logic to render the parsed JSON into the results cards.
**Tools Used:** JavaScript.
**Output:** Client-side upload and result display logic.
**Issues Faced:** Dropping a file was triggering the browser's default file-open behavior. Adding `preventDefault()` on `dragover` and `drop` events fixed it.
**Next Step:** Add JSON copy and PDF download buttons.

---

### Date: 2026-06-28
**Day Number:** Day 35
**Objective:** Add copy and download functionality to the frontend.
**Work Done:** Added clipboard copy for the JSON output and wired the "Download PDF" button to redirect to `/download_pdf?id=<id>`. Used `window.location.href` for the download trigger rather than AJAX, since browsers handle file download streams better that way. Added a "Copied!" text flash to confirm clipboard copy to the user.
**Tools Used:** JavaScript.
**Output:** Completed frontend with all interactions working.
**Issues Faced:** Initially tried triggering the download via AJAX fetch — browser blocked the file stream. Switching to `window.location.href` resolved it.
**Next Step:** Integrate frontend with backend completely.
**Screenshot to take:** Frontend home page loaded in browser.
**File naming:** `day-35-homepage-design.png`

---

## Week 6: Integration, Testing, Dataset Analysis & Final Documentation (Days 36–45)

### Date: 2026-06-29
**Day Number:** Day 36
**Objective:** Complete frontend-to-backend integration.
**Work Done:** Connected the HTML form's upload action to the Flask `/upload` endpoint. Tested with a real PDF — the file uploads, gets parsed, and the result cards display correctly in the browser. The parsed JSON is also saved to `outputs/` with a UUID-based filename. PDF download works.
**Tools Used:** Flask, JavaScript.
**Output:** Fully integrated and working web application.
**Issues Faced:** Session wasn't preserving the parsed profile ID between the upload and download requests. Fixed by saving the parsed JSON to `outputs/` and returning the file ID in the upload response, then using that ID for the download.
**Next Step:** Write unit tests.

---

### Date: 2026-06-30
**Day Number:** Day 37
**Objective:** Write unit tests in `test_parser.py`.
**Work Done:** Created `tests/test_parser.py` using Python's `unittest` framework. Wrote test cases for: text cleaner output, schema structure completeness, email extraction, phone extraction, name extraction with spaCy fallback, and citation-style publication matching. Covered 9 test cases in total.
**Tools Used:** Python unittest.
**Output:** Unit test file `tests/test_parser.py`.
**Issues Faced:** Import paths for backend modules weren't resolving from the test folder. Fixed by adding the parent path to `sys.path` at the top of the test file.
**Next Step:** Run tests and fix any failures.

---

### Date: 2026-07-01
**Day Number:** Day 38
**Objective:** Run the unit test suite and fix any issues.
**Work Done:** Ran `py -m unittest discover -s tests`. One test failed — a phone regex test with an international number containing extra spaces. Adjusted the regex pattern to handle that case. All 9 tests passed after the fix.
**Tools Used:** Python.
**Output:** Passing test suite.
**Issues Faced:** The phone pattern didn't account for spaces within the number body. Regex adjustment fixed it.
**Next Step:** Write the dataset explorer script.
**Screenshot to take:** All tests passing in terminal.
**File naming:** `day-38-unit-tests.png`

---

### Date: 2026-07-02
**Day Number:** Day 39
**Objective:** Write `dataset_explorer.py` for Kaggle data analysis.
**Work Done:** Created `scripts/dataset_explorer.py`. Uses Pandas to load the Kaggle structured CSV files and count education records, experience records, and skill tags. Also counts resumes by degree type (Ph.D., Master's, Bachelor's). Added a mock data fallback for when the CSVs are missing — displays a sample distribution chart using placeholder data.
**Tools Used:** Pandas, Python.
**Output:** `dataset_explorer.py` script.
**Issues Faced:** Missing dataset files caused a crash on the first run. Added error handling to fall back to mock data.
**Next Step:** Run the script and generate the skills distribution chart.

---

### Date: 2026-07-03
**Day Number:** Day 40
**Objective:** Run the dataset explorer and generate the skills distribution chart.
**Work Done:** Ran `py scripts/dataset_explorer.py`. Generated a bar chart of the top technical skills present in the Kaggle dataset and saved it as `data/skills_distribution.png`. Also printed summary counts — total profiles, education records, experience records, and skill links.
**Tools Used:** Pandas, Seaborn, Matplotlib.
**Output:** Skills distribution chart saved to `data/skills_distribution.png`.
**Issues Faced:** Matplotlib raised a thread-related warning at the end. Added `plt.close()` after saving the plot to handle it cleanly.
**Next Step:** Final UI polish and error handling.
**Screenshot to take:** Generated skills distribution chart.
**File naming:** `day-40-skills-distribution.png`

---

### Date: 2026-07-04
**Day Number:** Day 41
**Objective:** Improve frontend error handling and UI polish.
**Work Done:** Added notification banners to the frontend for invalid file types and upload failures. Configured the UI to reset properly after a failed upload. Fixed some layout issues on smaller screens using media query adjustments.
**Tools Used:** HTML, CSS, JavaScript.
**Output:** Improved error states in the frontend.
**Issues Faced:** On mobile-sized screens, some cards were overflowing. Adjusted flex direction in the media query.
**Next Step:** Add Tesseract status indicator to the dashboard.
**Screenshot to take:** Warning banner on invalid file drop.
**File naming:** `day-41-frontend-errors.png`

---

### Date: 2026-07-05
**Day Number:** Day 42
**Objective:** Add Tesseract availability indicator to the UI.
**Work Done:** Updated the `/` route in Flask to pass the `TESSERACT_AVAILABLE` status to the HTML template. Added a status badge in the header that shows "OCR Active" or "OCR Unavailable" depending on whether Tesseract is installed. This helps users understand upfront whether scanned PDFs will use real OCR or the fallback.
**Tools Used:** Python, Flask, HTML, CSS.
**Output:** Tesseract status badge in the dashboard header.
**Issues Faced:** None.
**Next Step:** Build and run the bulk validation suite.
**Screenshot to take:** Tesseract status badge displayed on dashboard.
**File naming:** `day-42-tesseract-badge.png`

---

### Date: 2026-07-06
**Day Number:** Day 43
**Objective:** Build the bulk testing script and run an initial batch.
**Work Done:** Created `bulk_tester.py`. The script generates 50 synthetic resumes — 25 as searchable digital PDFs and 25 as image-only scanned PDFs (with simulated OCR noise). Runs all 50 through the parser and logs which fields are extracted successfully. First run revealed that Tesseract was having trouble with small fonts on the scanned test PDFs.
**Tools Used:** PyMuPDF, ReportLab, Pillow, Python.
**Output:** Initial bulk test run with results log.
**Issues Faced:** OCR was failing on some scanned test PDFs because the synthetic text was rendered at too small a font size for Tesseract to read reliably.
**Next Step:** Fix rendering and re-run bulk tests.
**Screenshot to take:** Initial bulk test output in terminal.
**File naming:** `day-43-bulk-metrics.png`

---

### Date: 2026-07-07
**Day Number:** Day 44
**Objective:** Fix OCR rendering issues and improve parsing heuristics.
**Work Done:** Increased font size and line spacing in the synthetic scanned PDF generator so Tesseract could read the text more reliably. Also added two OCR-specific heuristics to `nlp_engine.py`: (1) a name line-joiner that merges split first/last names when Tesseract separates them onto different lines, and (2) a phone character correction map that fixes common OCR misreads like `S` → `5` and `{` → `(`.
**Tools Used:** Python, PIL, Tesseract, gc.
**Output:** Improved bulk test PDF generator and more robust parsing for OCR output.
**Issues Faced:** Memory usage was rising during bulk OCR runs. Added `del pix` and `gc.collect()` calls inside the page rendering loop to release memory after each page.
**Next Step:** Final bulk test run and documentation.
**Screenshot to take:** Terminal showing bulk test results.
**File naming:** `day-44-memory-release.png`

---

### Date: 2026-07-09
**Day Number:** Day 45
**Objective:** Run final bulk validation, fix email parsing bug, and compile all documentation.
**Work Done:**
- Ran the final 50-resume bulk validation suite. Results were encouraging — routing worked correctly for all test resumes, and name and phone extraction showed good consistency across the synthetic samples. OCR results varied slightly based on image quality, as expected.
- Identified and fixed an email extraction bug: some resumes with "E-mail:" labels (hyphenated) weren't being captured. Updated `extract_email()` with additional patterns to handle these variations and tested the fix.
- Fixed a parsing mismatch where some internship entries were being classified under Education. Updated section keyword lists to better separate education and experience entries.
- Compiled Fortnight Reports 1–3, the Final Report, and presentation slides.
- Updated schema to also capture `projects`, `achievements`, `certificates`, and `awards` fields, and updated the dashboard to display them.
**Tools Used:** Python, Markdown.
**Output:** Final bulk test results, fixed parser, complete project documentation.
**Issues Faced:** Email extraction was missing hyphenated label formats. Fixed with additional regex patterns.
**Next Step:** Submit project to supervisor.
**Screenshot to take:** Final bulk test output showing field extraction results.
**File naming:** `day-45-final-run.png`

---

### Date: 2026-05-28
**Day Number:** Follow-up parser fix
**Objective:** Improve extraction reliability for faculty application PDFs with boxed personal-details tables.
**Work Done:** Added a layout-aware faculty form helper in `backend/app/layout_parser.py` that reads the cleaned page text and maps labels to nearby values in the personal details table. Merged those layout hints into `backend/app/routes.py` so father name and husband name can be recovered when the NLP pass leaves a blank or placeholder value. Verified the fix on `outputs/test_kavitha.pdf`, where the father name is extracted as `D.Subrahmanyeswara Rao` and the husband name as `Dr.D.V.S.Chowdary`.
**Tools Used:** Python, pdfplumber, existing PDF sample.
**Output:** Parser improvement verified against the Kavitha faculty application PDF.
**Issues Faced:** The first attempt used fragmented word-level layout text and did not preserve the table row cleanly. Switching to `pdfplumber` plain page text resolved it.
**Next Step:** Extend the same approach to other faculty form variants and keep adding regressions.

---

*End of Daily Logbook — PS-I, JK Lakshmipat University, Jaipur*
