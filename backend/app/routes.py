import os
import json
import traceback
from flask import render_template, request, jsonify, send_file
from backend.app.utils import save_uploaded_file, normalize_extracted_data, OUTPUT_FOLDER
from backend.app.parser import parse_file
from backend.app.ocr_engine import extract_text_via_ocr, TESSERACT_AVAILABLE
from backend.app.nlp_engine import parse_resume_text
from backend.app.pdf_generator import generate_candidate_pdf

def register_routes(app):
    @app.route('/')
    def index():
        """Render the single page web application frontend."""
        return render_template('index.html', tesseract_available=TESSERACT_AVAILABLE)

    @app.route('/upload', methods=['POST'])
    @app.route('/process', methods=['POST'])
    def process_resume():
        """
        Endpoint to upload and process PDF resumes.
        Extracts raw text (using NLP for digital and OCR for scanned),
        extracts structured schema, saves JSON, and returns result.
        """
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Save file to uploads folder
        filepath = save_uploaded_file(file)
        if not filepath:
            return jsonify({"error": "Invalid file format. Only PDF files are allowed."}), 400
        try:
            # 1. Parse file structure and get type / scanned status
            parse_result = parse_file(filepath)
            if parse_result.get("error"):
                return jsonify({"error": parse_result["error"]}), 400

            file_type = parse_result["file_type"]
            is_scanned = parse_result["is_scanned"]
            raw_text = parse_result["raw_text"]
            layout_fields = parse_result.get("layout_fields") or {}

            print(f"[DEBUG] File: {file.filename}, Type: {file_type}, Scanned: {is_scanned}")
            print(f"[DEBUG] Raw text length: {len(raw_text)}, First 200 chars: {repr(raw_text[:200])}")

            # 2. Extract text (digital vs OCR route). Use hybrid fallback when digital text seems insufficient.
            extracted_text = raw_text
            extraction_method = "digital"

            if is_scanned and file_type == 'pdf':
                extraction_method = "ocr_scanned"
                extracted_text = extract_text_via_ocr(filepath)

            minimal_text_threshold = 150
            needs_hybrid = (not extracted_text) or (len(extracted_text.strip()) < minimal_text_threshold)
            if not needs_hybrid:
                preview = extracted_text.lower()
                if all(k not in preview for k in ["email", "phone", "contact", "education", "experience"]):
                    needs_hybrid = True

            if needs_hybrid:
                try:
                    ocr_text = extract_text_via_ocr(filepath)
                    combined_lines = []
                    seen = set()
                    for src in (extracted_text, ocr_text):
                        for ln in (src or "").splitlines():
                            s = ln.strip()
                            if not s:
                                continue
                            lower_line = s.lower()
                            if lower_line in seen:
                                continue
                            seen.add(lower_line)
                            combined_lines.append(s)
                    if combined_lines:
                        extracted_text = "\n".join(combined_lines)
                        extraction_method = "hybrid_digital_ocr"
                except Exception:
                    pass

            print(f"[DEBUG] Extraction method: {extraction_method}, Text length: {len(extracted_text)}")

            contact_idx = extracted_text.lower().find('contact')
            email_idx = extracted_text.lower().find('email')
            print(f"[DEBUG] Contact section index: {contact_idx}, Email keyword index: {email_idx}")

            if email_idx >= 0:
                start = max(0, email_idx - 100)
                end = min(len(extracted_text), email_idx + 300)
                print(f"[DEBUG] Text around 'Email' keyword:\n{repr(extracted_text[start:end])}\n")

            if contact_idx >= 0:
                end = min(len(extracted_text), contact_idx + 500)
                print(f"[DEBUG] Text from 'Contact' section:\n{repr(extracted_text[contact_idx:end])}\n")

            # 3. Process text through NLP engine
            structured_data = parse_resume_text(extracted_text)

            def _is_blank_or_placeholder(value):
                if value is None:
                    return True
                text = str(value).strip()
                if not text:
                    return True
                return text.lower() in {
                    'occupation', 'category', 'religion', 'place of birth',
                    'email id', 'mobile no.', 'mobile no', 'advt no',
                    'registration no', 'name in full', 'age'
                }

            for key, value in layout_fields.items():
                if value and _is_blank_or_placeholder(structured_data.get(key)):
                    structured_data[key] = value

            print(f"[DEBUG] Extracted email: '{structured_data.get('email', 'EMPTY')}'")
            print(f"[DEBUG] Extracted name: '{structured_data.get('name', 'EMPTY')}'")
            print(f"[DEBUG] Extracted phone: '{structured_data.get('phone', 'EMPTY')}'")
            print(f"[DEBUG] Full extracted data keys: {list(structured_data.keys())}")

            # 4. Normalize to fixed schema
            normalized_data = normalize_extracted_data(structured_data)

            # 5. Save structured data to outputs/ folder as JSON
            unique_id = os.path.basename(filepath).split('_')[0]
            json_filename = f"{unique_id}.json"
            json_filepath = os.path.join(OUTPUT_FOLDER, json_filename)

            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(normalized_data, f, indent=2, ensure_ascii=False)

            return jsonify({
                "id": unique_id,
                "file_name": file.filename,
                "file_type": file_type,
                "extraction_method": extraction_method,
                "tesseract_active": TESSERACT_AVAILABLE,
                "data": normalized_data
            })

        except Exception as e:
            # Print full traceback to console for immediate debugging
            print(f"Error processing resume: {e}")
            traceback.print_exc()
            # Also save a minimal crash log to logs/parser_crash.log for later inspection
            try:
                os.makedirs('logs', exist_ok=True)
                with open(os.path.join('logs', 'parser_crash.log'), 'a', encoding='utf-8') as lf:
                    lf.write('='*80 + '\n')
                    lf.write(f'File: {file.filename if "file" in locals() else "<unknown>"}\n')
                    lf.write(f'Path: {filepath if "filepath" in locals() else "<unknown>"}\n')
                    lf.write(traceback.format_exc())
                    lf.write('\n')
            except Exception:
                pass
            return jsonify({"error": f"An error occurred during resume parsing: {str(e)}"}), 500

    @app.route('/download_pdf', methods=['GET'])
    def download_pdf():
        """
        Generate and download the PDF report for a given profile ID.
        Queries the stored JSON data by ID.
        """
        profile_id = request.args.get('id')
        if not profile_id:
            return "Profile ID is required", 400
            
        # Secure profile ID to prevent path traversal
        profile_id = os.path.basename(profile_id)
        json_filename = f"{profile_id}.json"
        json_filepath = os.path.join(OUTPUT_FOLDER, json_filename)
        
        if not os.path.exists(json_filepath):
            return "Profile not found", 404
            
        try:
            # Read stored JSON profile
            with open(json_filepath, 'r', encoding='utf-8') as f:
                candidate_data = json.load(f)
                
            # Generate PDF file
            pdf_filename = f"{profile_id}_report.pdf"
            pdf_filepath = os.path.join(OUTPUT_FOLDER, pdf_filename)
            
            generate_candidate_pdf(candidate_data, pdf_filepath)
            
            # Return PDF file as an attachment
            return send_file(
                pdf_filepath,
                as_attachment=True,
                download_name=f"Candidate_Report_{profile_id}.pdf",
                mimetype='application/pdf'
            )
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return f"An error occurred during PDF report generation: {str(e)}", 500
