# Research Paper and Resource Summaries (Student-Level Review)
**Course Code:** PS1101 (Practice School I) | **Organization:** JK Lakshmipat University, Jaipur

This document summarizes the core technical resources and papers reviewed during Week 1 to establish the technical foundation for the parsing pipeline. The review was focused on practical implementation details suitable for a second-year engineering student.

## 1. Smith (2007) — "An Overview of the Tesseract OCR Engine"
- **Focus of Study:** Understood the underlying binarization, layout analysis, and LSTM character recognition process used by Tesseract.
- **Key Takeaways:** Tesseract works by identifying text blocks, lines, and character shapes. It is highly sensitive to image resolution and quality.
- **Practical Application:** I understood that directly sending low-resolution PDF renders to Tesseract produces severe spelling noise. I decided that when converting PDF pages to images for OCR, I must scale the render by at least 2.0 (effectively doubling the DPI) to give Tesseract clean, readable characters.

## 2. spaCy Named Entity Recognition (NER) Documentation
- **Focus of Study:** Studied spaCy's pre-trained NLP models (like `en_core_web_sm`) and their ability to detect entities like `PERSON` (names), `ORG` (institutions), and `GPE` (locations).
- **Key Takeaways:** spaCy is extremely fast and accurate for standard English text, but can misclassify headings or formatting artifacts. For example, a heading like "Curriculum Vitae" is sometimes tagged as a `PERSON`.
- **Practical Application:** I learned that while NER is excellent for extracting the candidate's name and university from the top of a CV, we must supplement it with regular expression heuristics and block-lists (e.g., ignoring words like "Resume" or "University") to maintain high accuracy.

## 3. LayoutLM: Pre-training of Text and Layout for Document Image Understanding (Conceptual Review)
- **Focus of Study:** Read the abstract and conceptual sections to understand how modern deep learning models combine textual tokens with 2D spatial coordinate coordinates (bounding boxes).
- **Key Takeaways:** Combining visual layout coordinates with language models drastically improves document understanding in forms and receipts where spatial alignment dictates the meaning of text.
- **Practical Application:** While LayoutLM is extremely powerful, it is too heavyweight for our current lab environment due to strict GPU hardware requirements. I decided to stick with a lightweight hybrid pipeline (PyMuPDF text extraction + spaCy + custom regex) which is robust, highly portable, and runs instantly on any standard CPU.

## 4. Practical Resume Parsing Heuristics (Technical Blog & Open-Source Reviews)
- **Focus of Study:** Researched practical developer guides on how to read PDFs and DOCX files in Python and structure the extracted text.
- **Key Takeaways:** Text extracted from PDFs is often jumbled, containing weird unicode bullets (like ``), smart quotes, and multiple consecutive empty lines.
- **Practical Application:** I recognized the critical need for a dedicated text-cleaning preprocessor. Before sending any extracted text to the NLP engine, we must normalize unicode encodings, standardize quotes, and collapse blank lines, which I will implement in `cleaner.py`.
