import argparse
import json
import os
import sys
import traceback
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Batch smoke test: resume -> structured -> faculty PDF.")
    parser.add_argument(
        "--input-dir",
        default=None,
        help="Folder containing PDF resumes. Defaults to backend/uploads.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Max resumes to test (0 = no limit).")
    parser.add_argument("--output-dir", default=None, help="Where to write PDFs + report.")
    parser.add_argument("--ocr", action="store_true", help="Enable OCR route for scanned PDFs.")
    parser.add_argument("--hybrid", action="store_true", help="Enable hybrid digital+OCR fallback when text is short.")
    parser.add_argument("--max-failures", type=int, default=50, help="How many failures to store in report.")
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Ensure `backend.app.*` imports work
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Imports after sys.path tweak
    from backend.app.parser import parse_file
    from backend.app.ocr_engine import extract_text_via_ocr, TESSERACT_AVAILABLE
    from backend.app.nlp_engine import parse_resume_text
    from backend.app.utils import normalize_extracted_data
    from backend.app.pdf_generator import generate_candidate_pdf

    default_input = os.path.join(project_root, "uploads")
    input_dir = args.input_dir or default_input
    if not os.path.isdir(input_dir):
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        return 2

    out_dir = args.output_dir or os.path.join(project_root, "outputs", "batch_test")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "pdfs"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "json"), exist_ok=True)

    # Discover PDFs
    pdfs = []
    for name in os.listdir(input_dir):
        if not name.lower().endswith(".pdf"):
            continue
        pdfs.append(os.path.join(input_dir, name))
    pdfs.sort()

    if args.limit and args.limit > 0:
        pdfs = pdfs[: args.limit]

    report = {
        "started_at": datetime.utcnow().isoformat() + "Z",
        "input_dir": input_dir,
        "count": len(pdfs),
        "ocr_enabled": bool(args.ocr),
        "hybrid_enabled": bool(args.hybrid),
        "tesseract_available": bool(TESSERACT_AVAILABLE),
        "failures": [],
        "pass_count": 0,
        "fail_count": 0,
    }

    # Same heuristic as your Flask route, to mirror production behavior.
    minimal_text_threshold = 150

    for idx, pdf_path in enumerate(pdfs, start=1):
        file_name = os.path.basename(pdf_path)
        unique_id = os.path.splitext(file_name)[0].split("_")[0]
        try:
            parse_result = parse_file(pdf_path)
            if parse_result.get("error"):
                raise RuntimeError(parse_result["error"])

            file_type = parse_result.get("file_type")
            is_scanned = bool(parse_result.get("is_scanned"))
            raw_text = parse_result.get("raw_text") or ""

            extracted_text = ""
            extraction_method = "nlp_digital"

            if is_scanned and file_type == "pdf":
                if not args.ocr:
                    # If OCR not enabled, treat as failure (so we know it would crash in prod config).
                    raise RuntimeError("Scanned PDF detected but OCR disabled for test.")
                extraction_method = "ocr_scanned"
                extracted_text = extract_text_via_ocr(pdf_path)
            else:
                extracted_text = raw_text

            needs_hybrid = False
            if args.hybrid:
                needs_hybrid = (not extracted_text) or (len(extracted_text.strip()) < minimal_text_threshold)
                if not needs_hybrid and extracted_text:
                    preview = extracted_text.lower()
                    if all(k not in preview for k in ["email", "phone", "contact", "education", "experience"]):
                        needs_hybrid = True
                if needs_hybrid:
                    ocr_text = extract_text_via_ocr(pdf_path)
                    combined_lines = []
                    seen = set()
                    for src in (extracted_text, ocr_text):
                        for ln in (src or "").splitlines():
                            s = ln.strip()
                            if not s:
                                continue
                            key = s.lower()
                            if key in seen:
                                continue
                            seen.add(key)
                            combined_lines.append(s)
                    extracted_text = "\n".join(combined_lines)
                    extraction_method = "hybrid_digital_ocr"

            structured_data = parse_resume_text(extracted_text)
            normalized_data = normalize_extracted_data(structured_data)

            # Light validations (production must not crash; correctness is harder to fully auto-check)
            if not normalized_data.get("name"):
                raise RuntimeError("Normalized data missing name")
            if normalized_data.get("education") is None:
                raise RuntimeError("Normalized data education is None")

            # Save JSON for debugging
            json_out = os.path.join(out_dir, "json", f"{unique_id}.json")
            with open(json_out, "w", encoding="utf-8") as f:
                json.dump(normalized_data, f, indent=2, ensure_ascii=False)

            pdf_out = os.path.join(out_dir, "pdfs", f"{unique_id}_report.pdf")
            generate_candidate_pdf(normalized_data, pdf_out)

            if not os.path.exists(pdf_out) or os.path.getsize(pdf_out) <= 0:
                raise RuntimeError("PDF generation produced empty/missing output.")

            report["pass_count"] += 1
            if idx % 10 == 0:
                print(f"[{idx}/{len(pdfs)}] PASS: {file_name}")

        except Exception as e:
            report["fail_count"] += 1
            err = {
                "file": file_name,
                "unique_id": unique_id,
                "error": str(e),
                "traceback": traceback.format_exc(limit=10),
            }
            if len(report["failures"]) < args.max_failures:
                report["failures"].append(err)
            print(f"[{idx}/{len(pdfs)}] FAIL: {file_name}: {e}", file=sys.stderr)

    report["finished_at"] = datetime.utcnow().isoformat() + "Z"
    report_out = os.path.join(out_dir, "batch_report.json")
    with open(report_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nBatch test finished. Pass: {report['pass_count']}, Fail: {report['fail_count']}")
    print(f"Report: {report_out}")

    return 1 if report["fail_count"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

