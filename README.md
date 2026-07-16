# Faculty Recruitment Portal

Faculty Recruitment Portal is a Flask-based resume parsing app for faculty hiring workflows. It accepts PDF resumes, extracts structured profile data from both digital and scanned documents, and generates a standardized candidate report PDF for review.

## What It Does

* Parses faculty resumes into a normalized JSON schema.
* Uses a hybrid extraction path: direct text parsing for digital PDFs and OCR fallback for scanned PDFs.
* Generates a committee-friendly PDF report from the extracted profile.
* Stores uploaded files and parsed outputs locally for review and debugging.

## Strengths

* Handles both text-based and scanned PDFs.
* Uses a fixed schema so downstream review is consistent.
* Includes layout-aware extraction for faculty application forms.
* Generates a downloadable report after parsing.
* Keeps debug-friendly JSON outputs in `outputs/`.

## Known Limitations

* PDF only: other file types are rejected.
* OCR quality depends on Tesseract and the source scan quality.
* Extraction accuracy may vary on unusual layouts, low-quality scans, or highly customized resumes.

## Setup

1. Create and activate a virtual environment on Windows:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR and make sure it is available in your system PATH.

4. Let the app download the spaCy English model automatically on first run if it is missing.

## Run

Start the application with:

```bash
python backend/app/main.py
```

The server runs at `http://127.0.0.1:5000`.

## Tutorial

1. Open the local app in your browser.
2. Upload a PDF resume using the upload panel.
3. The app will parse the file, extract structured data, and save a JSON result in `outputs/`.
4. If parsing succeeds, use the download option to generate the candidate report PDF.
5. Review the JSON and PDF outputs to confirm the extracted data is correct.

## Inputs And Outputs

* Uploaded PDFs are saved in `uploads/`.
* Parsed JSON files are saved in `outputs/`.
* Generated report PDFs are saved in `outputs/` as well.
* Temporary or diagnostic logs may be written to `logs/` during failures.

## Project Structure

* `backend/app/main.py`: Flask app entry point.
* `backend/app/routes.py`: Web routes for upload, processing, and PDF download.
* `backend/app/parser.py`: File parsing and document type handling.
* `backend/app/ocr_engine.py`: OCR extraction path for scanned PDFs.
* `backend/app/nlp_engine.py`: Resume text parsing and structured extraction.
* `backend/app/layout_parser.py`: Layout-aware field extraction for faculty forms.
* `backend/app/pdf_generator.py`: Candidate report generation.
* `backend/app/utils.py`: Upload handling, directories, and schema normalization.
* `tests/` and root `test_*.py` files: Focused checks and regression scripts.

## Testing

The repository contains several focused test scripts, including:

* `test_pipeline.py`
* `test_ocr_split.py`
* `tests/test_parser.py`
* `backend/test_api_new.py`
* `backend/test_comprehensive.py`

Run the relevant script directly when you want to verify a specific path.

## Handoff Notes

* The app is optimized for faculty resumes and application forms, not generic resume parsing.
* Review `outputs/` after test runs to inspect extracted JSON and generated PDFs.
* If OCR results are poor, confirm Tesseract is installed and the source PDF is readable.
* If a field is missing in the JSON, check both the NLP path and the layout-based fallback in the backend.
