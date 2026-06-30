"""
Lightweight layout-aware text extraction.

Features:
- Prefer a model-based layoutparser extraction if `layoutparser` is installed and the user opts in.
- Fallback: pdfplumber-based column detection and column-wise text ordering (no heavy deps).

Usage:
  from backend.app.layout_parser import extract_text_with_layout
  text = extract_text_with_layout('path/to/file.pdf')

This is designed to be small, dependency-light, and effective for common multi-column resumes.
"""
from typing import Dict, List
import pdfplumber
import re


def _page_words_center(page):
    words = page.extract_words(extra_attrs=['x0','x1','top','bottom'])
    centers = []
    for w in words:
        x0 = float(w.get('x0', 0))
        x1 = float(w.get('x1', x0))
        cx = (x0 + x1) / 2.0
        centers.append({'word': w, 'cx': cx})
    return centers


def _detect_column_boundaries(centers: List[dict], page_width: float, max_columns=3):
    """Detect column centers by splitting large gaps in x-centers.

    This simple heuristic groups word centers and splits when a gap > threshold*page_width.
    """
    if not centers:
        return [ (0.0, page_width) ]

    xs = sorted([c['cx'] for c in centers])
    if len(xs) == 1:
        return [ (0.0, page_width) ]

    # compute gaps between consecutive centers
    gaps = []
    for i in range(1, len(xs)):
        gaps.append((i, xs[i] - xs[i-1]))

    # threshold: any gap significantly bigger than typical gaps counts as a split candidate.
    # Use an adaptive threshold: max(0.18, mean_gap*3) of page width scaled, but not too small.
    mean_gap = sum(g for _, g in gaps) / len(gaps)
    # convert mean_gap (in points) to fraction of page_width
    mean_frac = mean_gap / page_width
    adaptive_frac = max(0.18, min(0.30, mean_frac * 3))
    thresh = adaptive_frac * page_width
    split_indices = [i for i, g in gaps if g > thresh]

    # limit number of splits so columns <= max_columns
    if len(split_indices) >= max_columns:
        split_indices = split_indices[:max_columns-1]

    # produce ranges
    boundaries = []
    split_points = []
    for idx in split_indices:
        # split after xs[idx-1], so boundary at midpoint
        boundary = (xs[idx-1] + xs[idx]) / 2.0
        split_points.append(boundary)

    splits = [0.0] + split_points + [page_width]
    for i in range(len(splits)-1):
        boundaries.append( (splits[i], splits[i+1]) )

    return boundaries


def _assign_words_to_columns(centers: List[dict], boundaries: List[tuple]):
    cols = [[] for _ in boundaries]
    for c in centers:
        cx = c['cx']
        for idx, (l, r) in enumerate(boundaries):
            if cx >= l and cx <= r:
                cols[idx].append(c['word'])
                break
    return cols


def _merge_small_or_sparse_columns(boundaries: List[tuple], cols: List[list], page_width: float):
    # Merge columns that are very narrow or contain very little text into neighboring columns.
    widths = [r - l for (l, r) in boundaries]
    merged_boundaries = []
    merged_cols = []
    i = 0
    while i < len(boundaries):
        w = widths[i]
        col = cols[i]
        # if column is very narrow (<15% page width) or has very few words, merge with neighbor
        narrow = w < 0.15 * page_width
        sparse = len(col) < 3
        if (narrow or sparse) and len(boundaries) > 1:
            # prefer merging into previous if exists, else next
            if merged_cols:
                # merge into previous
                prev_idx = len(merged_cols) - 1
                # extend boundary
                l_prev, _ = merged_boundaries[prev_idx]
                merged_boundaries[prev_idx] = (l_prev, boundaries[i][1])
                merged_cols[prev_idx].extend(col)
            else:
                # merge into next (if exists)
                if i + 1 < len(boundaries):
                    _, next_r = boundaries[i + 1]
                    merged_boundaries.append((boundaries[i][0], next_r))
                    merged_cols.append(col + cols[i+1])
                    i += 1  # skip the next since merged
                else:
                    # single column left, just keep
                    merged_boundaries.append(boundaries[i])
                    merged_cols.append(col)
        else:
            merged_boundaries.append(boundaries[i])
            merged_cols.append(col)
        i += 1

    return merged_boundaries, merged_cols


def _words_to_text_column(words: List[dict]):
    # order by top then x0 to rebuild lines
    if not words:
        return ''
    sorted_words = sorted(words, key=lambda w: (float(w.get('top', 0)), float(w.get('x0', 0))))
    lines = []
    current_top = None
    current_line = []
    for w in sorted_words:
        top = float(w.get('top', 0))
        text = w.get('text', '')
        if current_top is None:
            current_top = top
            current_line = [text]
        else:
            # if vertical gap significant, start a new line
            if abs(top - current_top) > 6:  # ~6 pts
                lines.append(' '.join(current_line))
                current_line = [text]
                current_top = top
            else:
                current_line.append(text)
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)


def extract_text_with_layout(pdf_path: str, use_layoutparser: bool=False) -> str:
    """Extract text from PDF with simple layout handling.

    If `use_layoutparser` is True and layoutparser is available, attempts model-based layout segmentation.
    Otherwise falls back to pdfplumber heuristic column detection.
    Returns concatenated text for all pages where columns are read left-to-right.
    """
    # try layoutparser approach if requested
    if use_layoutparser:
        try:
            import importlib
            lp = importlib.import_module('layoutparser')
            model = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config', extra_config = ["MODEL.DEVICE: cpu"])  # CPU-friendly
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    pil = page.to_image(resolution=150).original
                    layout = model.detect(pil)
                    # get text blocks labeled as Text
                    text_blocks = [b for b in layout if b.type == 'Text']
                    # sort by x1 then y1 to read left-to-right, top-to-bottom
                    text_blocks = sorted(text_blocks, key=lambda b: (b.block.x_1, b.block.y_1))
                    for blk in text_blocks:
                        bbox = blk.block
                        # perform OCR on crop using pdfplumber's text extraction fallback
                        # pdfplumber cannot OCR; use page.within_bbox
                        x0,y0,x1,y1 = bbox.x_1, bbox.y_1, bbox.x_2, bbox.y_2
                        page_crop = page.within_bbox((x0,y0,x1,y1))
                        text_parts.append(page_crop.extract_text() or '')
            return '\n\n'.join([t for t in text_parts if t])
        except Exception:
            # fallback to pdfplumber heuristic
            pass

    # pdfplumber heuristic fallback
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_width = page.width
            centers = _page_words_center(page)
            boundaries = _detect_column_boundaries(centers, page_width)
            cols = _assign_words_to_columns(centers, boundaries)
            # Merge tiny or sparse columns which often break logical blocks like experience/contact
            try:
                boundaries, cols = _merge_small_or_sparse_columns(boundaries, cols, page_width)
            except Exception:
                pass
            # convert each column to text, then join left->right
            col_texts = [_words_to_text_column(c) for c in cols]
            page_text = '\n\n'.join([ct for ct in col_texts if ct.strip()])
            if not page_text.strip():
                # fallback to full page extract
                text = page.extract_text() or ''
                all_text.append(text)
            else:
                all_text.append(page_text)
    return '\n\n'.join(all_text)


def _cluster_words_by_row(words: List[dict], y_tolerance: float = 4.5) -> List[List[dict]]:
    rows = []
    for word in sorted(words, key=lambda w: (float(w.get('top', 0)), float(w.get('x0', 0)))):
        top = float(word.get('top', 0))
        if not rows or abs(top - rows[-1][0]) > y_tolerance:
            rows.append((top, [word]))
        else:
            rows[-1][1].append(word)
    return [row_words for _, row_words in rows]


def _row_text(row_words: List[dict]) -> str:
    ordered = sorted(row_words, key=lambda w: float(w.get('x0', 0)))
    parts = [str(w.get('text', '')).strip() for w in ordered if str(w.get('text', '')).strip()]
    return re.sub(r"\s+", " ", ' '.join(parts)).strip()


def _clean_field_value(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", (value or '')).strip(" \t\r\n:-")
    if not cleaned:
        return ''
    if re.fullmatch(r"(?i)(occupation|age|category|religion|place of birth|advt no|registration no|email id|mobile no|name in full|dob)", cleaned):
        return ''
    return cleaned


def _looks_like_label(line: str) -> bool:
    candidate = re.sub(r"\s+", " ", (line or '')).strip().lower()
    if not candidate:
        return False
    return bool(re.search(r"\b(advt no|registration no|application for the post of|specialisation|name in full|dob|age|father'?s name|mother'?s name|nationality|place of birth|email id|mobile no\.?|gender/marital status|category|religion|husband name|other category|occupation)\b", candidate))


def _extract_label_value_from_lines(lines: List[str], label_patterns: List[str]) -> str:
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if not any(re.search(pattern, line_lower, re.IGNORECASE) for pattern in label_patterns):
            continue

        after_colon = line.split(':', 1)[1].strip() if ':' in line else ''
        after_colon = re.split(r"\boccupation\b|\bcategory\b|\breligion\b|\bplace of birth\b|\bemail id\b|\bmobile no\.?\b|\bhusband name\b|\bnationality\b", after_colon, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        candidate = _clean_field_value(after_colon)
        if candidate:
            return candidate

        # Some forms place the value on the next line, especially when the label is in a tiny cell.
        for next_line in lines[idx + 1: idx + 3]:
            next_candidate = _clean_field_value(next_line)
            if next_candidate and not _looks_like_label(next_candidate):
                return next_candidate

    return ''


def _extract_numeric_label_value_from_lines(lines: List[str], label_patterns: List[str]) -> str:
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        # Use word-boundary match to prevent matching 'age' inside words like 'management', 'language'
        if not any(re.search(r'\b' + pattern.strip('\\b') + r'\b', line_lower, re.IGNORECASE) for pattern in label_patterns):
            continue

        after_colon = line.split(':', 1)[1].strip() if ':' in line else ''
        match = re.search(r"\b(\d{1,3})\b", after_colon)
        if match:
            val = int(match.group(1))
            # Validate age is plausible (18-80)
            if 18 <= val <= 80:
                return match.group(1)

        for next_line in lines[idx + 1: idx + 3]:
            match = re.search(r"\b(\d{1,3})\b", next_line)
            if match:
                val = int(match.group(1))
                if 18 <= val <= 80:
                    return match.group(1)

    return ''


def _extract_row_value(row_text: str, label: str, next_labels: List[str]) -> str:
    pattern = rf"{label}\s*:\s*(.*?)(?=\s*(?:{'|'.join(next_labels)})\s*:|$)"
    match = re.search(pattern, row_text, re.IGNORECASE)
    if not match:
        return ''
    return _clean_field_value(match.group(1))


def extract_faculty_form_fields(pdf_path: str) -> Dict[str, str]:
    """Extract key faculty application fields by reading the PDF table layout.

    This is a small layout-aware helper for the application form template.
    It prefers the text positioned on the same row to the right of each label,
    which is more reliable than pure line-based OCR for boxed forms.
    """
    fields = {
        'advt_no': '',
        'registration_no': '',
        'post_applied_for': '',
        'specialisation': '',
        'name': '',
        'dob': '',
        'age': '',
        'father_name': '',
        'mother_name': '',
        'nationality': '',
        'place_of_birth': '',
        'email': '',
        'phone': '',
        'gender_marital_status': '',
        'category': '',
        'religion': '',
        'husband_name': '',
        'other_category': '',
    }

    page_texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:2]:
            page_text = page.extract_text() or ''
            if page_text.strip():
                page_texts.append(page_text)

    normalized_text = "\n".join(page_texts).strip()
    if not normalized_text:
        normalized_text = extract_text_with_layout(pdf_path, use_layoutparser=False)

    lines = [re.sub(r"\s+", " ", line).strip() for line in normalized_text.splitlines() if line.strip()]
    normalized_text = "\n".join(lines)

    line_field_patterns = {
        'advt_no': [r"advt no"],
        'registration_no': [r"registration no"],
        'post_applied_for': [r"application for the post of"],
        'specialisation': [r"specialisation"],
        'name': [r"name in full"],
        'dob': [r"dob"],
        'age': [r"age"],
        'father_name': [r"father['’]?s name", r"father name"],
        'mother_name': [r"mother['’]?s name", r"mother name"],
        'nationality': [r"nationality"],
        'place_of_birth': [r"place of birth"],
        'email': [r"email id"],
        'phone': [r"mobile no\.?"],
        'gender_marital_status': [r"gender/marital status"],
        'category': [r"category"],
        'religion': [r"religion"],
        'husband_name': [r"husband name"],
        'other_category': [r"other category"],
    }

    for key, label_patterns in line_field_patterns.items():
        if key == 'age':
            value = _extract_numeric_label_value_from_lines(lines, label_patterns)
        else:
            value = _extract_label_value_from_lines(lines, label_patterns)
        if value:
            fields[key] = value

    return fields
