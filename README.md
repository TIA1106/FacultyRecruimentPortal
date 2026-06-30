# Faculty Recruitment Portal

A comprehensive portal for managing faculty recruitment, parsing resumes (both text and scanned PDFs), and generating standardized candidate PDFs for review.

## Features

*   **Resume Parsing**: Advanced NLP-based extraction of candidate details from resumes using spaCy.
*   **OCR Support**: Handles both normal (text-based) and scanned PDFs using Tesseract.
*   **PDF Generation**: Standardized PDF output formatted for the recruitment committee, matching specific layout requirements.
*   **Robust Extraction**: Handles various edge cases in Indian academic resumes, including formatting quirks, tables, and varied section headers.

## Project Structure

*   `backend/`: Contains the Flask application, NLP engine, and PDF generation logic.
    *   `app/main.py`: Flask server entry point.
    *   `app/nlp_engine.py`: Resume parsing and information extraction.
    *   `app/pdf_generator.py`: Candidate PDF generation logic.
*   `data/`: Data storage.
*   `docs/`: Documentation.
*   `uploads/`: Directory for uploaded resumes.
*   `outputs/`: Directory for generated candidate PDFs.
*   `scripts/`: Utility scripts.
*   `tests/`: Unit and integration tests.

## Setup

1.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/Scripts/activate  # On Windows
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Ensure Tesseract OCR is installed and available in your system path.

4.  Run the Flask backend:
    ```bash
    python backend/app/main.py
    ```
