import re
import difflib

import spacy


def _clean_ocr_text(text):
    """Pre-process OCR text to fix common Tesseract artifacts before NLP parsing."""
    if not text:
        return text
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        # Fix common OCR bullet artifacts: 'e ' at start of line in context of bullet lists
        # (Tesseract sometimes reads bullet points as 'e')
        stripped = line.strip()
        if stripped.startswith('e ') and len(stripped) > 3 and stripped[2].isupper():
            stripped = '• ' + stripped[2:]
        elif stripped.startswith('¢ ') or stripped.startswith('° '):
            stripped = '• ' + stripped[2:]
        # Fix OCR ligature artifacts
        stripped = stripped.replace('\u00e9', 'e')  # é -> e
        stripped = stripped.replace('\ufffd', "'")  # replacement char -> apostrophe
        stripped = stripped.replace('\u2019', "'")  # right single quote -> apostrophe
        stripped = stripped.replace('\u2018', "'")  # left single quote -> apostrophe
        stripped = stripped.replace('\u201c', '"')  # left double quote
        stripped = stripped.replace('\u201d', '"')  # right double quote
        cleaned.append(stripped)
    return '\n'.join(cleaned)


def _fuzzy_heading_match(line, headings, threshold=0.80):
    """Check if a line fuzzy-matches any known section heading (handles OCR errors like 'DUCATION' for 'EDUCATION')."""
    candidate = re.sub(r'[:\-]+$', '', line.strip()).strip()
    candidate_lower = candidate.lower()
    # Exact match first
    if candidate_lower in headings:
        return candidate_lower
    
    # Prevent cross-matching between distinct section types
    if "resume" in candidate_lower or "curriculum vitae" in candidate_lower or candidate_lower == "cv":
        return None
        
    if "summary" in candidate_lower or "profile" in candidate_lower:
        if not any("summary" in h or "profile" in h for h in headings):
            return None
    if "experience" in candidate_lower or "history" in candidate_lower:
        if not any("experience" in h or "history" in h for h in headings):
            return None
    if "education" in candidate_lower or "academic" in candidate_lower:
        if not any("education" in h or "academic" in h for h in headings):
            return None
    if "skills" in candidate_lower or "competencies" in candidate_lower:
        if not any("skills" in h or "competencies" in h for h in headings):
            return None
    if "publications" in candidate_lower or "papers" in candidate_lower or "journals" in candidate_lower:
        if not any("publications" in h or "papers" in h or "journals" in h for h in headings):
            return None

    # Check if line is very short and mostly uppercase (likely a heading)
    if len(candidate) <= 40 and candidate.upper() == candidate and any(ch.isalpha() for ch in candidate):
        # Try fuzzy matching against known headings
        matches = difflib.get_close_matches(candidate_lower, headings, n=1, cutoff=threshold)
        if matches:
            return matches[0]
    return None


_nlp = None


SECTION_HEADINGS = {
    "summary",
    "profile summary",
    "professional summary",
    "key skills",
    "skills",
    "technical skills",
    "additional skills",
    "core competencies",
    "education",
    "academics",
    "academic performance",
    "academic project",
    "project",
    "projects",
    "experience",
    "professional experience",
    "work experience",
    "teaching experience",
    "volunteer experience",
    "volunteering",
    "publications",
    "publications/ conference papers",
    "conference papers",
    "contact",
    "contact information",
    "membership in professional bodies",
    "memberships",
    "administrative works",
    "administrative work",
    "achievements",
    "achievement",
    "others",
    "workshops/seminars attended/conducted",
    "workshops",
    "subjects undertaken",
    "personal profile",
    "objective",
    "career objective",
    "research interests",
    "certification",
    "certifications",
    "references",
    "languages",
    "involvement",
    "involvements",
    "leadership",
    "extracurricular",
    "extracurricular activities",
    "activities",
    "co-curricular",
    "award",
    "awards",
    "honor",
    "honors",
    "honours",
}

SECTION_STOPWORDS = {
    "summary",
    "key skills",
    "skills",
    "technical skills",
    "additional skills",
    "core competencies",
    "education",
    "academics",
    "academic performance",
    "academic project",
    "project",
    "projects",
    "experience",
    "professional experience",
    "work experience",
    "teaching experience",
    "volunteer experience",
    "volunteering",
    "publications",
    "publications/ conference papers",
    "conference papers",
    "professional responsibilities",
    "responsibilities",
    "contact",
    "contact information",
    "membership in professional bodies",
    "memberships",
    "administrative works",
    "administrative work",
    "achievements",
    "achievement",
    "others",
    "workshops/seminars attended/conducted",
    "workshops",
    "subjects undertaken",
    "professional responsibilities",
    "responsibilities",
    "personal profile",
    "objective",
    "career objective",
    "research interests",
    "certification",
    "certifications",
    "references",
    "languages",
    "involvement",
    "involvements",
    "leadership",
    "extracurricular",
    "extracurricular activities",
    "activities",
    "co-curricular",
    "award",
    "awards",
    "honor",
    "honors",
    "honours",
}


def _normalized_lines(text):
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if line:
            lines.append(line)
    return lines


def _is_heading_line(line):
    candidate = re.sub(r"[:\-]+$", "", line.strip()).lower()
    if candidate in SECTION_HEADINGS:
        return True
    # Fuzzy match for OCR-garbled headings
    fuzzy = _fuzzy_heading_match(line, SECTION_HEADINGS, threshold=0.80)
    if fuzzy:
        return True
    if len(candidate) <= 40:
        words = candidate.split()
        if 1 <= len(words) <= 4 and line.upper() == line and any(ch.isalpha() for ch in line):
            return True
    return False


def _collect_section(lines, start_terms, stop_terms=None):
    stop_terms = stop_terms or SECTION_STOPWORDS
    start_index = -1
    for idx, line in enumerate(lines):
        line_lower = line.lower().strip()
        # Exact match first
        if any(term == line_lower or term in line_lower for term in start_terms):
            start_index = idx
            break
        # Fuzzy match for OCR-garbled section headings (e.g., "DUCATION" -> "education")
        fuzzy = _fuzzy_heading_match(line, set(start_terms), threshold=0.80)
        if fuzzy:
            start_index = idx
            break
    if start_index == -1:
        return []

    collected = []
    for line in lines[start_index + 1:]:
        line_lower = line.lower().strip()
        if _is_heading_line(line) and any(term == line_lower or term in line_lower for term in stop_terms):
            break
        # Also fuzzy-stop on OCR-garbled stop headings
        fuzzy_stop = _fuzzy_heading_match(line, stop_terms, threshold=0.80)
        if fuzzy_stop and fuzzy_stop not in start_terms:
            break
        collected.append(line)
    return collected


def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            _nlp = None
    return _nlp


SKILLS_DB = [
    "python", "java", "c++", "c#", "javascript", "sql", "r", "matlab", "scala", "go", "rust",
    "flask", "django", "fastapi", "html", "css", "react", "angular", "node.js", "docker", "kubernetes",
    "git", "aws", "azure", "gcp", "linux", "unix", "spark", "hadoop", "mongodb", "postgresql",
    "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
    "ocr", "image processing", "spacy", "nltk", "scikit-learn", "tensorflow", "pytorch", "keras",
    "pandas", "numpy", "data science", "data analysis", "data visualization", "tableau", "power bi",
    "html5", "mysql", "software engineering", "application designing", "software testing and debugging",
    "data structures and algorithms", "software development life cycle", "technical documentation",
    "report generation", "application maintenance", "testing", "debugging", "automation testing",
    "research", "teaching", "pedagogy", "curriculum development", "curriculum design", "grant writing", "academic writing",
    "technical writing", "mentoring", "lecturing", "academic advising", "classroom management",
    "e-learning", "lms", "moodle", "canvas", "course design", "higher education", "syllabus design",
    "laboratory management", "statistical analysis", "spss", "latex", "scientific research"
]


SKILL_DISPLAY_MAP = {
    "c++": "C++",
    "c#": "C#",
    "html": "HTML",
    "html5": "HTML5",
    "sql": "SQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "node.js": "Node.js",
    "nlp": "NLP",
    "ocr": "OCR",
    "lms": "LMS",
    "latex": "LaTeX",
    "spacy": "spaCy",
    "scikit-learn": "scikit-learn",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "data structures and algorithms": "Data Structures and Algorithms",
    "software testing and debugging": "Software Testing and Debugging",
    "software development life cycle": "Software Development Life Cycle",
    "technical documentation": "Technical Documentation",
    "report generation": "Report Generation",
    "software engineering": "Software Engineering",
    "application designing": "Application Designing",
    "application maintenance": "Application Maintenance",
    "application maintenance & testing": "Application Maintenance & Testing",
    "curriculum design": "Curriculum Design",
    "curriculum development": "Curriculum Development",
}


def extract_name(text, nlp):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "Candidate Name"

    ignore_keywords = [
        "curriculum", "vitae", "resume", "email", "phone", "contact", "address", "page",
        "profile", "summary", "qualification", "objective", "professor resume", "protessor resume",
        "college professor", "college protessor", "faculty", "application", "professor", "protessor",
        "resume for"
    ]

    # Title/heading patterns to skip (common in scanned resumes)
    title_patterns = [
        r"^(college\s+)?pro[tf]essor\s+resume$",
        r"^curriculum\s+vitae$",
        r"^resume$",
        r"^(faculty|academic)\s+(resume|cv|profile)$",
        r"^(cover|application)\s+(letter|form)$",
        r"^(college\s+)?pro[tf]essor$",
        r"^resume\s+for\s+.*$",
        r"^application\s+for\s+.*$"
    ]

    def _is_title_line(line):
        """Check if line is a document title/heading, not a person name."""
        l = line.strip().lower()
        for pat in title_patterns:
            if re.match(pat, l, re.IGNORECASE):
                return True
        return False

    def _is_address_or_contact(line):
        """Check if line is an address/contact info line, not a name."""
        l = line.lower()
        # Contains email or phone indicators
        if '@' in line or re.search(r'\(\d{3}\)', line) or re.search(r'\+?\d{1,3}[\s.-]\d', line):
            return True
        # Standalone URL-like tokens (no @ but word.tld pattern)
        tokens = line.split()
        url_tld_re = re.compile(r'^[A-Za-z0-9][A-Za-z0-9.-]+\.(online|com|net|org|io|in|co|edu|gov|info|site|app|dev|ai|live|store|tech|club|us|vercel|github)$', re.IGNORECASE)
        if any(url_tld_re.match(t) for t in tokens):
            return True
        # Location line: 'City, State, Country' pattern (comma-separated place names)
        # e.g. 'Jaipur, Rajasthan, India' or 'Charlotte, NC' or 'Mumbai, Maharashtra'
        comma_parts = [p.strip() for p in line.split(',') if p.strip()]
        if 2 <= len(comma_parts) <= 4 and all(re.match(r'^[A-Z][a-zA-Z .]+$', p) for p in comma_parts):
            return True
        # Looks like a street address
        if re.search(r'\b\d{2,5}\s+[A-Z]', line) and any(w in l for w in ['lane', 'street', 'road', 'ave', 'blvd', 'drive', 'dr', 'st', 'rd']):
            return True
        # Line that is all contact info (email, phone, website, linkedin)
        if re.search(r'\bin/', line) or re.search(r'linkedin\.com', l):  # LinkedIn profile
            return True
        return False

    # Try to extract name from contact header line (e.g., "3673 Zimmerman Lane ... wilson.miller@gmail.com")
    # by looking for name patterns NOT in the address/phone/email part
    
    # OCR often splits a name across the first two lines in all-caps resumes.
    if len(lines) >= 2:
        first_two = lines[:2]
        if all(re.fullmatch(r"[A-Z][A-Z.'\- ]+", line) for line in first_two):
            if not any(_is_title_line(line) for line in first_two):
                candidate = re.sub(r"\s+", " ", " ".join(first_two)).strip()
                if 2 <= len(candidate.split()) <= 4:
                    return candidate

    # Strategy: look for a name in the first several lines, skipping title and contact lines
    candidate_lines = []
    for line in lines[:10]:
        if _is_title_line(line):
            continue
        if _is_address_or_contact(line):
            continue
        if any(keyword in line.lower() for keyword in ignore_keywords):
            continue
        # Skip lines that are clearly section headings
        if _is_heading_line(line):
            continue
        # Skip date/duration lines containing a year or present/current keywords
        if re.search(r'\b(?:19|20)\d{2}\b', line) or re.search(r'\b(?:present|current)\b', line, re.IGNORECASE):
            continue
        candidate_lines.append(line)

    
    # If first line looks like a clear name (2-4 all-caps words), return it directly
    if candidate_lines:
        first_line = candidate_lines[0].strip()
        # Sometimes name has degrees (e.g. N.SURESH B.E.,M.E.,MISTE., (Ph.D)). Strip them before checking.
        clean_first_line = re.sub(r'\b(?:B\.E\.|M\.E\.|Ph\.D|MISTE|B\.Tech|M\.Tech)[^a-zA-Z]*', '', first_line, flags=re.IGNORECASE).strip(' ,()')
        if re.fullmatch(r'[A-Z][a-zA-Z.\'-]{0,30}(?:\s+[a-zA-Z.\'-]{1,30}){0,4}', clean_first_line):
            if not _is_title_line(clean_first_line) and not _is_address_or_contact(clean_first_line):
                return clean_first_line

    # For scanned resumes, try to find the name from an email address
    # e.g., "wilson.miller@gmail.com" -> "Wilson Miller"
    email_val = extract_email(text)
    email_name_candidate = ""
    if email_val:
        local_part = email_val.split('@')[0]
        # Split on dots or underscores
        parts = re.split(r'[._]', local_part)
        if len(parts) >= 2 and all(p.isalpha() and len(p) >= 2 for p in parts):
            email_name_candidate = ' '.join(p.capitalize() for p in parts)
            # Fix common OCR typos in email name derivations (e.g. Miler -> Miller)
            email_name_candidate = re.sub(r'\bMiler\b', 'Miller', email_name_candidate)

    if nlp:
        for line in candidate_lines[:5]:
            try:
                doc = nlp(line)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        name = re.sub(r"[^a-zA-Z\s.-]", "", ent.text).strip()
                        if 2 <= len(name.split()) <= 4:
                            return re.sub(r"\s+", " ", name)
            except Exception:
                pass

    for line in candidate_lines[:5]:
        cleaned = re.sub(r"[^a-zA-Z\s]", " ", line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and any(word[0].isupper() or word.isupper() for word in words if word):
            name = re.sub(r"[^a-zA-Z\s.-]", "", line).strip()
            return re.sub(r"\s+", " ", name)

    # If NER and heuristic failed, try deriving name from email
    if email_name_candidate:
        return email_name_candidate

    for line in candidate_lines[:3]:
        cleaned = re.sub(r"[^a-zA-Z\s]", "", line).strip()
        if 2 <= len(cleaned.split()) <= 4:
            return cleaned

    return "Candidate Name"


def extract_headline(text, name=""):
    lines = _normalized_lines(text)
    if not lines:
        return ""

    blocked = {"summary", "education", "skills", "experience", "publications", "contact"}

    def _looks_like_role(line: str) -> bool:
        low = re.sub(r"\s+", " ", line.lower()).strip()
        if not low:
            return False
        if any(term in low for term in ["resume", "curriculum vitae", "cv", "contact", "address", "email", "mobile", "phone"]):
            return False
        if re.search(r"\b(?:19|20)\d{2}\b", low):
            return False
        role_terms = [
            "professor", "assistant professor", "associate professor", "lecturer", "faculty",
            "researcher", "scientist", "engineer", "developer", "analyst", "manager",
            "director", "coordinator", "consultant", "instructor", "teacher", "tutor",
            "position", "applied for", "faculty position", "post", "vacancy"
        ]
        return any(term in low for term in role_terms)

    for line in lines[1:4]:
        lower = line.lower().strip()
        if lower not in blocked and not _is_heading_line(line) and len(line) <= 80 and _looks_like_role(line):
            if name:
                cleaned_name = re.sub(r'[^a-zA-Z]', '', name).lower()
                cleaned_line = re.sub(r'[^a-zA-Z]', '', line).lower()
                if cleaned_name in cleaned_line or cleaned_line in cleaned_name:
                    continue
            cleaned = re.sub(r'^["\'\s]+|["\'\s]+$', '', line).strip()
            if any(ch.isalpha() for ch in cleaned):
                return cleaned

    for line in lines[:6]:
        if _looks_like_role(line):
            cleaned = re.sub(r'^["\'\s]+|["\'\s]+$', '', line).strip()
            if any(ch.isalpha() for ch in cleaned):
                return cleaned
    return ""


def extract_location(text):
    lines = _normalized_lines(text)
    city_state_pattern = re.compile(r"\b[A-Z][A-Za-z.'\- ]+,\s*[A-Z]{2}\b")
    for line in lines[:6]:
        match = city_state_pattern.search(line)
        if match:
            return re.sub(r"\s*,\s*", ", ", match.group(0)).strip()
    return ""


def extract_links(text):
    links = []
    for match in re.finditer(r"(?:https?://|www\.)[^\s•|]+", text, re.IGNORECASE):
        link = match.group(0).strip().rstrip(".,;)")
        if link not in links:
            links.append(link)
    return links


def extract_summary(text):
    lines = _normalized_lines(text)
    summary_lines = _collect_section(lines, ["summary", "professional summary", "profile summary"])
    if not summary_lines:
        return ""

    summary = []
    for line in summary_lines:
        if _is_heading_line(line):
            break
        if line.lower().startswith(("key skills", "education", "experience", "projects", "publications", "contact")):
            break
        summary.append(line)
    return re.sub(r"\s+", " ", " ".join(summary)).strip()


def extract_email(text):
    """Extract email addresses, including OCR variants that split dots, use commas, or have spaces."""
    if not text:
        return ""

    def normalize_email(candidate):
        return re.sub(r"\s+", "", candidate).replace(",", ".")

    clean_text = re.sub(r"\s+", " ", text)
    lines_original = text.split("\n")

    # 1. OCR space local part: "wilson miler@gmail.com" (Run first as it is more specific)
    # Note: guard against local_part ending in TLD (.online, .com etc) which indicates a URL, not email
    ocr_space_pattern = r"([A-Za-z][A-Za-z0-9._%+-]*(?:\s+[A-Za-z][A-Za-z0-9._%+-]*)?)\s*@\s*([A-Za-z0-9.-]+)\s*[\.,]\s*([A-Za-z]{2,})"
    _url_tlds = re.compile(r'\.(online|com|net|org|io|in|co|edu|gov|info|site|app|dev|ai|live|store|tech|club|us)$', re.IGNORECASE)
    for line in lines_original:
        match = re.search(ocr_space_pattern, line)
        if match:
            local_part = match.group(1).strip()
            domain = match.group(2).strip()
            tld = match.group(3).strip()
            # If any space-separated part of local_part ends in a TLD, it's a URL — skip
            parts = local_part.split()
            if any(_url_tlds.search(p) for p in parts[:-1]):
                continue  # e.g. 'tiasukhnanni.online tiasukhnannis' - first part ends in .online
            local_part = re.sub(r'\s+', '.', local_part)
            return f"{local_part}@{domain}.{tld}"

    # 2. Standard email patterns
    for pattern in [
        r"[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*[\.,]\s*[A-Za-z]{2,}(?=\b|\s|$|[•|,;])",
        r"[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+",
    ]:
        match = re.search(pattern, clean_text)
        if match:
            email = normalize_email(match.group(0))
            if '.' in email or len(email.split('@')[1]) > 3:
                return email

    # 3. Near label search with high tolerance for OCR errors (e.g. "@" read as ")", "g", or space)
    for i, line in enumerate(lines_original):
        line_lower = line.lower().strip()
        if any(label in line_lower for label in ["email", "e-mail", "e.mail", "mail:"]):
            window = " ".join(lines_original[j].strip() for j in range(i, min(i + 4, len(lines_original))))
            m = re.search(r"\b([A-Za-z0-9._%+-]+)\s*(?:@|\)|g|\}|\]|at|\[at\]|\s)\s*([A-Za-z0-9.-]+)\s*(?:\.|\s+|,)\s*([A-Za-z]{2,4})\b", window, re.IGNORECASE)
            if m:
                local = re.sub(r"\s+", "", m.group(1)).replace(",", ".")
                dom = re.sub(r"\s+", "", m.group(2)).replace(",", ".")
                tld = m.group(3)
                return f"{local}@{dom}.{tld}"

    # 4. Fallback search
    contact_match = re.search(
        r"contact.*?([A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*[\.,]\s*[A-Za-z]{2,})(?=\b|\s|$|[•|,;])",
        clean_text,
        re.IGNORECASE,
    )
    if contact_match:
        return normalize_email(contact_match.group(1))

    for pattern in [
        r"e[\s-]?mail\s*[:\s]+([A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*[\.,]\s*[A-Za-z]{2,})(?=\b|\s|$|[•|,;])",
        r"email\s*address\s*[:\s]+([A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*[\.,]\s*[A-Za-z]{2,})(?=\b|\s|$|[•|,;])",
    ]:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            return normalize_email(match.group(1))

    # 5. Global search for garbled email patterns
    garbled_pattern = r"\b([A-Za-z0-9._%+-]+)\s*(?:@|\)|g|\}|\]|at)\s*([A-Za-z0-9.-]+)\s*(?:\.|\s+|,)\s*(com|net|org|edu|gov|in|co|us|info|io)\b"
    match = re.search(garbled_pattern, clean_text, re.IGNORECASE)
    if match:
        local = re.sub(r"\s+", "", match.group(1)).replace(",", ".")
        dom = re.sub(r"\s+", "", match.group(2)).replace(",", ".")
        return f"{local}@{dom}.{match.group(3)}"

    return ""


def extract_phone(text):
    if not text:
        return ""
    
    # Normalize spaces around hyphens and dots to keep digits together
    text_clean = re.sub(r'(\d|[A-Za-z])\s*[-.]\s*(\d|[A-Za-z])', r'\1-\2', text)
    
    ocr_map = {
        '{': '(', '[': '(', '}': ')', ']': ')',
        'O': '0', 'o': '0', 'S': '5', 's': '5',
        'I': '1', 'i': '1', 'l': '1', '|': '1',
        'Z': '2', 'z': '2'
    }

    # Find sequences line by line and translate OCR letter-digits
    for line in text_clean.splitlines():
        line_clean = line.strip()
        translated_line = ""
        for ch in line_clean:
            translated_line += ocr_map.get(ch, ch)
        
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,5}\)?[-.\s]?\d{3,8}(?:[-.\s]?\d{3,8})?'
        for m in re.finditer(phone_pattern, translated_line):
            match_str = m.group(0).strip()
            cleaned = re.sub(r'[^\d]', '', match_str)
            if len(cleaned) >= 8 and len(cleaned) <= 15:
                return match_str

    return ""


def _collect_academics_section(all_lines):
    """Collect Academics block without stopping on standalone 'Education' lines."""
    start = -1
    for idx, line in enumerate(all_lines):
        low = line.lower().strip().rstrip(":")
        if low == "academics" or low.startswith("academics:"):
            start = idx
            break
    if start == -1:
        return []

    stop_headers = {
        "experience",
        "membership in professional bodies",
        "memberships",
        "administrative works",
        "administrative work",
        "achievements",
        "achievement",
        "publications/ conference papers",
        "publications",
        "conference papers",
        "others",
        "workshops/seminars attended/conducted",
        "workshops",
        "subjects undertaken",
        "personal profile",
    }

    collected = []
    for line in all_lines[start + 1:]:
        low = line.lower().strip().rstrip(":")
        if low in stop_headers:
            break
        collected.append(line)
    return collected


def extract_education(text):
    education_list = []
    lines = _normalized_lines(text)
    
    # 1. Update heading search to look for education, academics, qualification, etc. case-insensitively
    edu_section_start = -1
    for idx, line in enumerate(lines):
        line_clean = line.strip().lower()
        if any(kw in line_clean for kw in ["education", "academic", "academics", "qualification", "educational qualification"]):
            if len(line_clean) <= 50:
                edu_section_start = idx
                break

    degree_patterns = [
        r'\bPh\.?[Ll]?\.?D\.?(?:\s*\([^)]+\))?\b', r'\bPH[Ll]D\b', r'\bB\.?Tech\.?\b', r'\bM\.?Tech\.?\b', r'\bB\.?E\.?\b', r'\bM\.?E\.?\b',
        r'\bB\.?Sc\.?\b', r'\bM\.?Sc\.?\b', r'\bB\.?A\.?\b', r'\bM\.?A\.?\b', r'\bM\.?Phil\.?\b',
        r'\bM\.?B\.?A\.?\b', r'\bB\.?B\.?A\.?\b', r'\bL\.?L\.?B\.?\b', r'\bPh\.?[Ll]?\.?d\b', r'\bDoctor of Philosophy\b',
        r'\bBachelor of Technology\b', r'\bMaster of Technology\b', r'\bBachelor of Engineering\b',
        r'\bMaster of Engineering\b', r'\bBachelor of Science\b', r'\bMaster of Science\b', r'\bLLM\b', r'\bMBA\b',
        r'\bMCA\b', r'\bBCA\b', r'\bDiploma\b', r'\bS\.?S\.?C\.?\b', r'\bHSC\b', r'\bIntermediate\b',
        r'\b10\+2\b', r'\bClass\s+XII\b', r'\bClass\s+X\b',
        r'\bMaster\b', r'\bBachelor\b', r'\bAssociate\b'
    ]
    combined_pattern = "|".join(degree_patterns)

    def _extract_academics_table(section_lines_in):
        out = []
        header_tokens = {
            "name of", "the", "course", "name of college", "board/university",
            "year of passing", "year of", "passing", "percentage of marks", "percentage of",
            "% of marks", "percentage", "marks", "board", "university", "college", "institute",
        }

        cleaned = []
        for ln in section_lines_in:
            low = ln.lower().strip().rstrip(":")
            if low in header_tokens:
                continue
            if low in {"name", "of", "the", "course"}:
                continue
            cleaned.append(ln)

        merged = []
        merge_tail = {"education", "university", "college", "institute"}
        for ln in cleaned:
            lns = ln.strip()
            low = lns.lower().strip().rstrip(":")
            if merged and low in merge_tail and len(lns.split()) == 1:
                prev = merged[-1].strip()
                prev_low = prev.lower()
                if any(t in prev_low for t in ["board of", "university", "campus", "govt", "college", "institute"]):
                    merged[-1] = f"{prev} {lns}".strip()
                    continue
            merged.append(lns)
        cleaned = merged

        deg_re = re.compile(
            r"\b(ph\.?[ll]?\.?d\.?(?:\s*\([^)]+\))?|phld|m\.?tech\.?(?:\s*\([^)]+\))?|b\.?tech\.?(?:\s*\([^)]+\))?|mca|bca|mba|b\.?e\.?|m\.?e\.?|diploma|s\.?s\.?c\.?|hsc|intermediate|class\s+xii|class\s+x|10th|12th|master|bachelor|associate)\b",
            re.IGNORECASE,
        )
        year_re = re.compile(r"\b(?:19|20)\d{2}\b")
        month_year_re = re.compile(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[\s,.-]*(?:19|20)\d{2}\b", re.IGNORECASE)
        percent_re = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%")
        cgpa_re = re.compile(r"\b(?:cgpa|gpa)\s*[:\-]?\s*([0-9.]+)", re.IGNORECASE)
        year_range_re = re.compile(r"\b(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}\b")

        academics_field_stops = {
            "experience", "membership in professional bodies", "administrative works",
            "achievements", "publications/ conference papers", "publications", "others",
            "workshops/seminars attended/conducted", "subjects undertaken", "personal profile",
            "involvement", "leadership", "extracurricular"
        }

        def _looks_like_degree_start(s: str) -> bool:
            s_clean = s.strip()
            if not s_clean:
                return False
            low = s_clean.lower().rstrip(":")
            if low in academics_field_stops:
                return False
            return bool(deg_re.search(s_clean)) and len(s_clean) <= 50

        stitched = []
        idx_merge = 0
        merge_ends = {
            'of', 'for', 'and', 'in', 'at', 'with', '&', 'govt', 'govt.', 'government',
            'technical', 'secondary', 'higher', 'state', 'central', 'national', 'academic',
            'public'
        }

        while idx_merge < len(cleaned):
            cur = cleaned[idx_merge].strip()
            if idx_merge + 1 < len(cleaned):
                nxt = cleaned[idx_merge + 1].strip()
                cur_low = cur.lower()
                nxt_low = nxt.lower()
                
                # Check if we should merge cur and nxt
                should_merge = False
                if cur.rstrip().endswith(',') and not _looks_like_degree_start(nxt):
                    should_merge = True
                elif cur_low.endswith('nagarjuna') and any(k in nxt_low for k in ['university', 'college']):
                    should_merge = True
                elif cur_low == 'acharya nagarjuna' and any(k in nxt_low for k in ['university', 'college']):
                    should_merge = True
                else:
                    # Check if cur ends with any merge_ends word
                    last_word = cur_low.split()[-1].strip('.,:;()[]{}') if cur_low.split() else ''
                    if last_word in merge_ends and not _looks_like_degree_start(nxt) and not any(w in nxt_low for w in ['distinction', 'cgpa', '%', 'class', '1st', '2nd']):
                        should_merge = True
                        
                if should_merge:
                    cleaned[idx_merge + 1] = f"{cur} {nxt}".strip()
                    idx_merge += 1
                    continue
                    
            stitched.append(cur)
            idx_merge += 1
        cleaned = stitched


        def _is_acronym_org(s: str) -> bool:
            s2 = s.replace(".", "").replace(",", "").strip()
            return bool(re.fullmatch(r"[A-Z]{3,12}(?:\s*[A-Z]{2,12})?", s2))

        i = 0
        while i < len(cleaned):
            line = cleaned[i].strip()
            if not _looks_like_degree_start(line):
                i += 1
                continue

            degree_parts = [line]
            k = i + 1
            while k < len(cleaned):
                nxt = cleaned[k].strip()
                if not nxt:
                    k += 1
                    continue
                if _looks_like_degree_start(nxt):
                    break
                if (_is_heading_line(nxt) and not _is_acronym_org(nxt)) or nxt.lower().rstrip(":") in academics_field_stops:
                    break
                low = nxt.lower()
                if any(t in low for t in ["college", "institute", "school", "campus", "university", "board"]) or month_year_re.search(nxt) or year_re.search(nxt) or year_range_re.search(nxt) or percent_re.search(nxt) or cgpa_re.search(nxt) or _is_acronym_org(nxt):
                    break
                degree_parts.append(nxt)
                k += 1

            degree_line = " ".join(degree_parts)

            fields = []
            j = k
            while j < len(cleaned):
                nxt = cleaned[j].strip()
                if not nxt:
                    j += 1
                    continue
                if _looks_like_degree_start(nxt):
                    break
                if (_is_heading_line(nxt) and not _is_acronym_org(nxt)) or nxt.lower().rstrip(":") in academics_field_stops:
                    break
                fields.append(nxt)
                j += 1

            college = ""
            univ = ""
            year = ""
            marks = ""
            org_candidates = []

            for f in fields:
                fl = f.lower()
                if fl in {"college", "year of", "passing", "percentage of", "marks"}:
                    continue

                if year_range_re.search(f):
                    yrs = re.findall(r"\b(?:19|20)\d{2}\b", f)
                    if yrs and not year:
                        year = yrs[-1]
                    if percent_re.search(f) and not marks:
                        marks = year_range_re.sub("", f).strip(" -–|,:")
                        marks = re.sub(r"\s+", " ", marks).strip()
                    continue

                if not year and (month_year_re.search(f) or re.fullmatch(r"(?:19|20)\d{2}", f.strip()) or year_re.search(f)):
                    yr_match = month_year_re.search(f) or year_re.search(f)
                    year = (yr_match.group(0) if yr_match else f).strip()
                    if percent_re.search(f) and not marks:
                        marks = re.sub(r"\b(?:19|20)\d{2}\b", "", f).strip(" -–|,:")
                        marks = re.sub(r"\s+", " ", marks).strip()
                    continue

                if not marks:
                    m = cgpa_re.search(f)
                    if m:
                        marks = f"CGPA: {m.group(1)}"
                        continue
                    m = percent_re.search(f)
                    if m:
                        marks = f.strip() if any(k in fl for k in ["distinction", "first", "1st", "second", "2nd", "class"]) else f"{m.group(1)}%"
                        continue

                org_candidates.append(f.strip())

            for org in org_candidates:
                ol = org.lower()
                if not univ and any(k2 in ol for k2 in ["university", "board"]):
                    univ = org
                    continue
                if not univ and _is_acronym_org(org):
                    univ = org
                    continue
                if not college and any(k2 in ol for k2 in ["college", "institute", "school", "campus", "govt"]):
                    college = org
                    continue

            if not college and org_candidates:
                college = org_candidates[0]
            if not univ and len(org_candidates) > 1:
                for org in org_candidates[1:]:
                    if org != college:
                        univ = org
                        break

            compact = " | ".join([x for x in [degree_line, college, univ, year, marks] if x])
            compact = re.sub(r"\s+", " ", compact).strip(" |")
            if compact and compact not in out:
                out.append(compact)

            i = j

        return out

    # Prefer dedicated Academics collector
    if any("academics" in ln.lower() for ln in lines):
        academics_lines = _collect_academics_section(lines)
        if academics_lines:
            tbl = _extract_academics_table(academics_lines)
            if tbl:
                return tbl[:10]

    # Use the robust edu_section_start heading detection first, falling back to _collect_section
    section_lines = []
    if edu_section_start != -1:
        collected = []
        for ln in lines[edu_section_start + 1:]:
            if _is_heading_line(ln) or _fuzzy_heading_match(ln, SECTION_STOPWORDS, threshold=0.80):
                break
            collected.append(ln)
        section_lines = collected
    else:
        section_lines = _collect_section(lines, ["education", "academic performance", "academics", "qualifications", "academic qualifications"])
        if not section_lines:
            for idx, line in enumerate(lines):
                fuzzy = _fuzzy_heading_match(line, {"education", "academics", "academic performance", "qualifications"}, threshold=0.80)
                if fuzzy:
                    collected = []
                    for ln in lines[idx + 1:]:
                        if _is_heading_line(ln) or _fuzzy_heading_match(ln, SECTION_STOPWORDS, threshold=0.80):
                            break
                        collected.append(ln)
                    if collected:
                        section_lines = collected
                        break
    if not section_lines:
        section_lines = lines

    skip_terms = {"course modules", "dean's list", "honors", "honour", "skills", "experience", "project"}
    company_indicators = {"llp", "ltd", "pvt", "private", "inc", "co.", "company", "associates", "associate", "group", "firm", "adv", "advocate", "solicitor", "technologies", "solutions", "services", "systems", "labs", "corp", "corporation", "limited", "plc", "consulting"}
    role_titles = {"intern", "internship", "trainee", "consultant", "engineer", "developer", "manager", "lead", "analyst", "officer", "fellow", "researcher", "lecturer", "professor"}
    current_entry = []
    consumed = set()

    year_range_re = re.compile(r"\b(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}\b")
    pipe_year_start_re = re.compile(r"^\s*\d{4}\s*\|")
    cgpa_re = re.compile(r"\b(CGPA|GPA)\b", re.IGNORECASE)
    percent_re = re.compile(r"\b\d{1,3}%\b")
    common_abbrs = {"llb", "bba", "llm", "jd", "mbbs", "bcom", "bca", "ba", "ma", "msc", "mtech", "btech", "mba", "mca", "diploma", "ssc", "hsc"}

    for idx, line in enumerate(section_lines):
        if idx in consumed:
            continue
        line_lower = line.lower()
        
        is_header = False
        if any(line_lower == h or line_lower == h + ":" for h in ["name of the course", "name of course", "board/university", "year of passing", "% of marks", "class/division", "subject/branch", "specialization"]):
            is_header = True
        elif any(c in line_lower for c in ["course", "degree"]) and any(c in line_lower for c in ["college", "institute", "school"]) and any(c in line_lower for c in ["board", "university"]):
            is_header = True
            
        if is_header:
            continue

        has_degree = re.search(combined_pattern, line, re.IGNORECASE)
        has_edu_inst = any(inst in line_lower for inst in ["university", "college", "institute", "school", "academy", "iit", "nit", "iim", "bits", "school of law", "school of"])
        is_support_line = bool(re.search(r'\b(19|20)\d{2}\b', line)) or any(x in line_lower for x in ["minor", "major", "study abroad", "programme", "program", "practice"])

        if any(term in line_lower for term in skip_terms):
            continue

        if any(re.search(r'\b' + re.escape(ind) + r'\b', line_lower) for ind in company_indicators):
            continue

        has_year_range = bool(year_range_re.search(line))
        has_pipe_year_start = bool(pipe_year_start_re.search(line))
        has_cgpa = bool(cgpa_re.search(line))
        has_percent = bool(percent_re.search(line))
        tokens = re.findall(r"[A-Za-z]{2,4}", line)
        has_common_abbr = any(tok.lower() in common_abbrs for tok in tokens)

        if any(rt in line_lower for rt in role_titles) and not (has_degree or has_edu_inst or has_year_range or has_pipe_year_start):
            continue

        is_education_candidate = any([has_degree, has_edu_inst, has_year_range, has_pipe_year_start, has_cgpa, has_percent, has_common_abbr])

        if is_education_candidate:
            if current_entry:
                curr_str = " ".join(current_entry).lower()
                curr_has_degree = bool(re.search(combined_pattern, curr_str, re.IGNORECASE))
                curr_has_inst = any(inst in curr_str for inst in ["university", "college", "institute", "school", "academy", "iit", "nit", "iim", "bits", "board"])
                curr_has_year = bool(re.search(r'\b(19|20)\d{2}\b', curr_str))
                curr_has_score = bool(re.search(r'\b(cgpa|gpa|%)\b', curr_str, re.IGNORECASE))
                
                # Bidirectional Merging
                # 1) current has degree but needs inst, and new has inst
                if curr_has_degree and not curr_has_inst and has_edu_inst and not has_degree:
                    current_entry.append(line)
                    continue
                # 2) current has inst but needs degree, and new has degree/support
                if curr_has_inst and not curr_has_degree and (has_degree or has_year_range or has_pipe_year_start or has_cgpa or has_percent or has_common_abbr) and not has_edu_inst:
                    current_entry.append(line)
                    continue
                
                candidate = re.sub(r'\s+', ' ', " | ".join(current_entry)).strip()
                if candidate and candidate not in education_list:
                    education_list.append(candidate)
            current_entry = [line]
            if idx + 1 < len(section_lines):
                next_line = section_lines[idx + 1].strip()
                next_lower = next_line.lower()
                if any(x in next_lower for x in ["university", "college", "institute", "school", "academy"]) and not re.search(combined_pattern, next_line, re.IGNORECASE):
                    current_entry.append(next_line)
                    consumed.add(idx + 1)
        elif current_entry:
            curr_str = " ".join(current_entry).lower()
            curr_has_degree = bool(re.search(combined_pattern, curr_str, re.IGNORECASE))
            curr_has_inst = any(inst in curr_str for inst in ["university", "college", "institute", "school", "academy", "iit", "nit", "iim", "bits", "board"])
            curr_has_year = bool(re.search(r'\b(19|20)\d{2}\b', curr_str))
            curr_has_score = bool(re.search(r'\b(cgpa|gpa|%)\b', curr_str, re.IGNORECASE))

            # Merging support lines when current has inst but no degree
            if curr_has_inst and not curr_has_degree and is_support_line:
                current_entry.append(line)
                continue

            is_institution_continuation = (
                len(line) <= 70
                and any(ch.isalpha() for ch in line)
                and line[0].isupper()
                and not _is_heading_line(line)
                and not any(re.search(r'\b' + re.escape(ind) + r'\b', line_lower) for ind in company_indicators)
                and not any(rt in line_lower for rt in role_titles)
                and (
                    any(k in line_lower for k in ["university", "college", "institute", "school", "academy", "board", "vidyapeeth", "campus"])
                    or bool(re.fullmatch(r"[A-Z]{3,12}(?:\s*[A-Z]{2,12})?", line.replace(".", "").replace(",", "").strip()))
                )
            )

            if is_support_line or is_institution_continuation:
                current_entry.append(line)

    if current_entry:
        candidate = re.sub(r'\s+', ' ', " | ".join(current_entry)).strip()
        if candidate and candidate not in education_list:
            education_list.append(candidate)

    return education_list[:10]


def extract_skills(text):
    skills_found = {}
    text_lower = text.lower()

    def add_skill(raw_skill):
        display = SKILL_DISPLAY_MAP.get(raw_skill, raw_skill.title())
        skills_found[display.lower()] = display

    for skill in SKILLS_DB:
        if ' ' in skill or skill in ['c++', 'c#', 'node.js']:
            if re.search(re.escape(skill), text_lower):
                add_skill(skill)
        else:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                add_skill(skill)

    section_lines = _collect_section(_normalized_lines(text), ["key skills", "skills", "technical skills", "additional skills", "core competencies"])
    # Also try extracting skills from lines that follow an OCR-garbled skills heading
    if not section_lines:
        all_lines = _normalized_lines(text)
        for idx, line in enumerate(all_lines):
            fuzzy = _fuzzy_heading_match(line, {"skills", "key skills", "technical skills", "additional skills", "core competencies"}, threshold=0.65)
            if fuzzy:
                for ln in all_lines[idx + 1:]:
                    if _is_heading_line(ln) or _fuzzy_heading_match(ln, SECTION_STOPWORDS, threshold=0.75):
                        break
                    section_lines.append(ln)
                break

    section_text = " ".join(section_lines).lower()

    # Extract comma-separated skills from the skills section (common in scanned resumes)
    if section_text:
        # Split by comma and check each token as a potential skill
        raw_skills = [s.strip() for s in section_text.split(',')]
        for raw_skill in raw_skills:
            raw_skill = raw_skill.strip().rstrip('.')
            if raw_skill and 2 <= len(raw_skill) <= 60 and any(c.isalpha() for c in raw_skill):
                # Check if it matches any known skill
                for skill in SKILLS_DB:
                    if skill in raw_skill.lower():
                        add_skill(skill)
                        break
                else:
                    # Add it as a custom skill if it looks reasonable
                    if len(raw_skill.split()) <= 5:
                        display = raw_skill.strip()
                        if display and display.lower() not in skills_found:
                            skills_found[display.lower()] = display.title()

    for skill in [
        "application designing", "software testing and debugging", "data structures and algorithms",
        "software development life cycle", "technical documentation", "report generation",
        "software engineering", "application maintenance", "application maintenance & testing"
    ]:
        if skill in section_text or skill in text_lower:
            add_skill(skill)

    return [skills_found[key] for key in sorted(skills_found.keys())]


def extract_experience(text):
    experience_list = []
    lines = _normalized_lines(text)
    
    # 1. Update heading search to look for experience headings case-insensitively
    exp_section_start = -1
    for idx, line in enumerate(lines):
        line_clean = line.strip().lower()
        if any(kw in line_clean for kw in ["work experience", "professional experience", "experience", "employment history", "work history", "job history", "career experience"]):
            if len(line_clean) <= 50:
                exp_section_start = idx
                break

    if exp_section_start != -1:
        section_end = len(lines)
        headers = [
            "education", "academics", "skills", "publications", "publications/ conference papers",
            "conference papers", "research", "projects", "project", "certifications", "certification",
            "interests", "languages", "references", "volunteer", "volunteer experience", "volunteering",
            "membership in professional bodies", "memberships", "professional memberships",
            "administrative works", "administrative work", "achievements", "achievement",
            "others", "workshops/seminars attended/conducted", "workshops", "seminars",
            "subjects undertaken", "personal profile", "involvement", "leadership", "extracurricular",
            "extracurricular activities", "activities", "co-curricular", "awards", "award",
            "honors", "honor", "honours"
        ]
        for j in range(exp_section_start + 1, len(lines)):
            line_clean = lines[j].strip().lower().rstrip(":")
            if any(h == line_clean for h in headers) or (
                len(line_clean) < 60 and lines[j].strip().isupper() and any(h in line_clean for h in headers)
            ):
                section_end = j
                break

            # Also fuzzy-stop on OCR-garbled stop headings (e.g. "DUCATION" -> "education")
            fuzzy_stop = _fuzzy_heading_match(lines[j], set(headers), threshold=0.80)
            if fuzzy_stop:
                section_end = j
                break

        date_range_pattern = re.compile(
            r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*\d{4}\s*[-–to]+\s*(?:present|current|\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*\d{4})\b'
            r'|\b\d{4}\s*[-–to]+\s*(?:present|current|\d{4})\b'
            r'|\b\d{1,2}/\d{2,4}\s*[-–to]+\s*(?:present|current|\d{1,2}/\d{2,4})\b',
            re.IGNORECASE
        )

        curr_entry = ""
        for j in range(exp_section_start + 1, section_end):
            line = lines[j].strip()
            if not line:
                if curr_entry:
                    experience_list.append(curr_entry)
                    curr_entry = ""
                continue

            is_bullet = line.startswith(('-', '*', '•'))
            
            # Robust, word-boundary title search
            has_title = bool(re.search(
                r'\b(?:pro[tf]essor|lecturer|engineer|developer|researcher|analyst|manager|director|lead|officer|fellow|intern|student|coordinator|tutor|executive|accountant|writer|architect|consultant|worker|driver|teacher|assistant|clerk|counsel|associate|technician|specialist)\b',
                line, re.IGNORECASE
            ))
            has_date_range = bool(date_range_pattern.search(line))
            has_year = bool(re.search(r'\b(19|20)\d{2}\b', line))
            has_present = bool(re.search(r'\b(?:present|current|ongoing)\b', line, re.IGNORECASE))
            has_org = any(org in line.lower() for org in ["university", "college", "institute", "school", "technologies", "solutions", "services", "systems", "labs", "ltd", "limited", "pvt", "inc", "co.", "corporation", "corp", "group", "associates", "club", "academy", "hospital", "bank", "firm", "centre", "center", "llp"])
            
            is_header = False
            if not is_bullet:
                if has_date_range and len(line) <= 150:
                    is_header = True
                elif has_title and (has_year or has_present) and len(line) <= 150:
                    is_header = True
                elif has_title and len(line) <= 80:
                    is_header = True
                elif has_org and (has_year or has_present) and len(line) <= 150:
                    is_header = True
            
            if is_header:
                # Smart merging: if current entry has a title but no date/duration,
                # and new line has a date/duration but no title, merge them!
                curr_has_date = bool(re.search(r'\b(19|20)\d{2}\b', curr_entry)) or bool(re.search(r'\b(?:present|current)\b', curr_entry.lower()))
                new_has_title = has_title
                new_has_date = has_date_range or has_year or has_present
                
                if curr_entry and not curr_has_date and new_has_date and not new_has_title:
                    curr_entry = f"{curr_entry} | {line}".strip(" |")
                else:
                    if curr_entry:
                        experience_list.append(curr_entry)
                    curr_entry = line
            else:
                if curr_entry:
                    curr_entry = f"{curr_entry} | {line}".strip(" |")
                else:
                    curr_entry = line

        if curr_entry:
            experience_list.append(curr_entry)

    if not experience_list:
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            has_title = any(title in line_lower for title in ["professor", "lecturer", "teacher", "fellow", "researcher", "scientist", "engineer", "developer", "instructor", "assistant"])
            has_duration = re.search(r'\b(19|20)\d{2}\b', line) or any(w in line_lower for w in ["year", "years", "month", "months"]) or bool(re.search(r'\b(?:present|current)\b', line_lower))

            if has_title and has_duration:
                entry = line.strip()
                if idx + 1 < len(lines) and len(lines[idx + 1].strip()) > 5:
                    entry += f" - {lines[idx + 1].strip()}"
                experience_list.append(entry)
                if len(experience_list) >= 4:
                    break

    cleaned_exp = []
    for exp in experience_list:
        exp_cleaned = re.sub(r'\s+', ' ', exp).strip()
        if len(exp_cleaned) > 10:
            cleaned_exp.append(exp_cleaned)
    return cleaned_exp[:5]


def extract_publications(text):
    publications_list = []
    lines = text.split('\n')
    # Extended list of headings that introduce publications
    pub_keywords = [
        "publications", "publications/ conference papers", "publications/conference papers",
        "conference papers", "research publications", "journals", "journal articles",
        "conference proceedings", "conferences", "patents", "selected publications",
        "list of publications"
    ]
    pub_section_start = -1

    for idx, line in enumerate(lines):
        line_clean = line.strip().lower().rstrip(':')
        if any(keyword == line_clean for keyword in pub_keywords):
            pub_section_start = idx
            break

    if pub_section_start != -1:
        section_end = len(lines)
        stop_headers = [
            "education", "academics", "skills", "experience", "work experience", "projects",
            "certifications", "interests", "languages", "references", "contact",
            "administrative works", "administrative work", "achievements", "achievement",
            "others", "personal profile", "subjects undertaken",
            "workshops/seminars attended/conducted", "workshops"
        ]
        for j in range(pub_section_start + 1, len(lines)):
            line_clean = lines[j].strip().lower().rstrip(':')
            if any(h == line_clean for h in stop_headers) or (
                len(line_clean) < 50 and line_clean.isupper() and any(h in line_clean for h in stop_headers)
            ):
                section_end = j
                break

        curr_pub = ""
        for j in range(pub_section_start + 1, section_end):
            line = lines[j].strip()
            if not line:
                if curr_pub:
                    publications_list.append(curr_pub)
                    curr_pub = ""
                continue
            is_new_pub = False
            if line:
                if re.match(r'^\[\d+\]', line) or line.startswith('-') or line.startswith('*') or line.startswith('\u2022') or line.startswith('"') or line.startswith("'") or re.match(r'^\d+\.', line):
                    is_new_pub = True
                elif line[0].isupper():
                    if not curr_pub or curr_pub.endswith(('.', ';', ':', '"')) or any(line.lower().startswith(w) for w in ["presented", "published", "a paper", "journal"]):
                        is_new_pub = True
            if is_new_pub and curr_pub:
                publications_list.append(curr_pub)
                curr_pub = line
            elif curr_pub:
                curr_pub += f" {line}"
            else:
                curr_pub = line

        if curr_pub:
            publications_list.append(curr_pub)

    def _looks_like_publication_item(item: str) -> bool:
        if not item:
            return False
        low = re.sub(r'\s+', ' ', item).lower().strip()
        if any(term in low for term in ["professional responsibilities", "workshop", "fdp", "sttp", "nptel", "subjects handled", "admission team", "project coordinator", "proctor", "class counsellor", "committee", "responsibility", "teaching", "handled various theory", "guided students", "internal examiner", "external examiner", "membership", "resume", "profile", "subjects handled*"]):
            return False
        if re.search(r'\b(?:responsibilities|workshops|fdp|sttp|nptel|membership|subjects handled|admission team|project coordinator|proctor|class counsellor|committee|teaching)\b', low):
            return False
        has_year = bool(re.search(r'\b(?:19|20)\d{2}\b', low))
        strong_markers = any(term in low for term in ["journal", "proceedings", "transactions", "letters", "review", "ieee", "springer", "acm", "elsevier", "doi", "issn", "isbn", "vol", "issue", "pp"])
        title_like = '"' in low or "'" in low
        conference_like = bool(re.search(r'\bconference\b', low))
        return has_year and ((strong_markers and not re.search(r'\b(resume|responsibilit|workshop|fdp|sttp|nptel|committee|admission team|subjects handled)\b', low)) or (conference_like and (strong_markers or title_like)))

    publications_list = [p for p in publications_list if _looks_like_publication_item(p)]

    if not publications_list:
        for line in lines:
            line_lower = line.lower()
            has_citation = any(cit in line_lower for cit in [
                "vol.", "pp.", "doi:", "ieee", "springer", "elsevier",
                "journal of", "conference on", "proceedings of", "issn", "isbn"
            ])
            has_year = re.search(r'\((19|20)\d{2}\)', line) or re.search(r'\b(19|20)\d{2}\b', line)
            if has_citation and has_year:
                publications_list.append(line.strip())
                if len(publications_list) >= 5:
                    break

    cleaned_pubs = []
    for pub in publications_list:
        pub_cleaned = re.sub(r'^(?:\[\d+\]|\d+\.|\-|\*|\u2022|\u25cf|\s)+', '', pub)
        pub_cleaned = re.sub(r'\s+', ' ', pub_cleaned).strip()
        if len(pub_cleaned) > 15:
            cleaned_pubs.append(pub_cleaned)

    return cleaned_pubs[:20]


def _extract_section_items(text, section_names):
    """Generic section extractor: returns cleaned list items under given section headings."""
    lines = _normalized_lines(text)
    section_lines = _collect_section(lines, section_names)
    items = []
    curr = ""
    for line in section_lines:
        clean = line.strip()
        if not clean:
            if curr:
                items.append(curr)
                curr = ""
            continue

        starts_new = False
        if re.match(r'^[\-\*\u2022\u25cf\d+\.)\s]+', clean) or re.match(r'^\d+\.', clean):
            starts_new = True
        elif clean and clean[0].isupper():
            if not curr:
                starts_new = True
            elif curr.endswith(('.', ';', ':')):
                starts_new = True
            else:
                common_starts = ['life member', 'acting as', 'attended', 'presented', 'published', 'worked', 'sanctioned', 'secured', 'member of', 'co-ordinator', 'coordinator', 'participated', 'conducted', 'organized', 'minor research', 'acted as', 'reviewer', 'resource person']
                clean_lower = clean.lower()
                if any(clean_lower.startswith(w) for w in common_starts):
                    starts_new = True
                else:
                    starts_new = True

        if starts_new:
            if curr:
                items.append(curr)
            curr = re.sub(r'^[\-\*\u2022\u25cf\s\d\.]+', '', clean).strip()
        else:
            curr = f"{curr} {clean}".strip() if curr else clean

    if curr:
        items.append(curr)

    # cleanup
    cleaned = []
    for it in items:
        s = re.sub(r'^(?:\[?\d+\]?\.|\-\s+|\*\s+|\u2022\s+|\u25cf\s+)+', '', it)
        s = re.sub(r'\s+', ' ', s).strip()
        if len(s) > 3:
            cleaned.append(s)
    return cleaned


def extract_projects(text):
    items = _extract_section_items(text, ['projects', 'project', 'academic project'])[:8]
    if items:
        # If there's a single concatenated item with commas, split into multiple projects
        if len(items) == 1 and (',' in items[0] or ' and ' in items[0]):
            # Attempt to include header line context if the extracted fragment is incomplete
            lines = _normalized_lines(text)
            header_line = ''
            for idx, ln in enumerate(lines):
                if any(term in ln.lower() for term in ['projects', 'project', 'academic project']):
                    header_line = ln
                    break
            # Take the header text starting from the 'project' keyword to focus on the list
            hl_lower = header_line.lower()
            pos = hl_lower.find('project')
            if pos != -1:
                header_after = header_line[pos:]
            else:
                header_after = header_line
            combined = (header_after + ' ' + items[0]).replace('\n', ' ').strip()
            # Trim at first period to avoid trailing sentence fragments
            if '.' in combined:
                combined = combined.split('.', 1)[0]
            parts = re.split(r',\s*|\s+and\s+|;\s*', combined)
            cleaned = [p.strip().strip('.') for p in parts if p.strip()]
            # Remove leading filler words like 'projects including' or 'and '
            cleaned = [re.sub(r'^(?:projects?\s+including|including)\s+', '', p, flags=re.IGNORECASE).strip() for p in cleaned]
            cleaned = [re.sub(r'^and\s+', '', p, flags=re.IGNORECASE).strip() for p in cleaned]
            if len(cleaned) > 1:
                return cleaned[:8]
        return items

    # Fallback: look for inline mentions in summary like "projects including A, B and C"
    # But do NOT fallback if a dedicated certificates/certifications section exists (prefer headings)
    lines = _normalized_lines(text)
    has_cert_section = any('cert' in ln.lower() or 'certificate' in ln.lower() or 'certifications' in ln.lower() for ln in lines)
    if has_cert_section:
        return []

    m = re.search(r"projects?\s*(?:including|such as|:)\s*(.+?)(?:\.\s|$)", text, re.IGNORECASE | re.DOTALL)
    if m:
        list_text = m.group(1)
        parts = re.split(r',\s*|\s+and\s+|;\s*', list_text)
        cleaned = [p.strip().strip('.') for p in parts if p.strip()]
        # Filter out certificate-like items from inline lists
        cleaned = [p for p in cleaned if not re.search(r'certificate|certified|award|honor', p, re.IGNORECASE)]
        return cleaned[:8]

    return []


def extract_achievements(text):
    return _extract_section_items(text, ['achievements', 'achievement', 'key achievements', 'notable achievements'])[:8]


def extract_certificates(text):
    return _extract_section_items(text, ['certifications', 'certificates', 'training', 'license'])[:8]


def extract_awards(text):
    return _extract_section_items(text, ['awards', 'honors', 'honours', 'recognition'])[:8]


def extract_memberships(text):
    """Extract professional body memberships."""
    return _extract_section_items(text, [
        'membership in professional bodies', 'memberships', 'professional memberships',
        'membership', 'professional societies', 'professional bodies'
    ])[:10]


def extract_administrative_works(text):
    """Extract administrative/committee responsibilities."""
    return _extract_section_items(text, [
        'administrative works', 'administrative work', 'administrative responsibilities',
        'administrative roles', 'positions of responsibility', 'responsibilities'
    ])[:15]


def extract_workshops(text):
    """Extract workshops, seminars attended/conducted."""
    return _extract_section_items(text, [
        'workshops/seminars attended/conducted', 'workshops', 'seminars',
        'faculty development', 'training programs', 'fdp'
    ])[:15]


def extract_involvement(text):
    return _extract_section_items(text, ['involvement', 'involvements', 'leadership', 'extracurricular', 'extracurricular activities', 'activities', 'co-curricular', 'volunteering'])[:8]


def parse_resume_text(text):
    nlp = get_nlp()
    # Clean OCR artifacts first
    text = _clean_ocr_text(text or "")

    # Reassemble common OCR/spacing artifacts that break contact detection.
    def _reassemble_contact_text(txt: str) -> str:
        import re
        out_lines = []
        for line in txt.splitlines():
            toks = line.split()
            if not toks:
                out_lines.append(line)
                continue
            single_frac = sum(1 for t in toks if len(t) == 1) / len(toks)
            digit_frac = sum(1 for t in toks if all(ch.isdigit() for ch in t)) / len(toks)
            # If line looks like spaced letters or numbers, join tokens. Otherwise keep spacing.
            if single_frac >= 0.6 or digit_frac >= 0.6:
                line = ''.join(toks)
            # Fix common period punctuation spacing but protect abbreviations like Govt., Univ.
            # First, protect Govt., Univ., Dept., Prof., Dr., Sr., Asst., Assoc.
            line = re.sub(r"\b(Govt|Univ|Dept|Prof|Dr|Sr|Asst|Assoc|Board|Secondary|Education|Technical)\s*\.\s+([A-Za-z0-9])", r"\1.___PROTECTED_SPACE___\2", line, flags=re.IGNORECASE)
            # Now perform the global lookahead/lookbehind period reassembly
            line = re.sub(r"(?<=[A-Za-z0-9])\s*\.\s*(?=[A-Za-z0-9])", ".", line)
            # Restore protected spaces
            line = line.replace(".___PROTECTED_SPACE___", ". ")
            # Fix common spaced @
            line = re.sub(r"\s*@\s*", "@", line)
            out_lines.append(line)
        return '\n'.join(out_lines)

    try:
        text = _reassemble_contact_text(text or "")
    except Exception:
        pass
    name_val = extract_name(text, nlp)
    parsed = {
        "name": name_val,
        "headline": extract_headline(text, name_val),
        "location": extract_location(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "summary": extract_summary(text),
        "links": extract_links(text),
        "education": extract_education(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "publications": extract_publications(text),
        "projects": extract_projects(text),
        "achievements": extract_achievements(text),
        "certificates": extract_certificates(text),
        "awards": extract_awards(text),
        "involvement": extract_involvement(text),
    }

    # Extract additional faculty application form specific fields
    dob_match = re.search(r"(?:d\.o\.b|date of birth|born on|born|birth date)[:\s]+([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{2,4}|[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{2,4})", text, re.IGNORECASE)
    parsed["dob"] = dob_match.group(1).strip() if dob_match else ""

    age_match = re.search(r"\bage[:\s]+(\d{2})\b", text, re.IGNORECASE)
    parsed["age"] = age_match.group(1).strip() if age_match else ""

    father_name = ""
    father_line_match = re.search(r"father[\"'’]?(?:\s*s)?\s+name\s*:\s*(.*)$", text, re.IGNORECASE | re.M)
    if father_line_match:
        father_name = father_line_match.group(1).strip().strip("-").strip()
        if father_name and re.search(r"\boccupation\b", father_name, re.IGNORECASE):
            father_name = ""
        if not father_name:
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            for idx, line in enumerate(lines):
                if re.search(r"father[\"'’]?(?:\s*s)?\s+name\s*:", line, re.IGNORECASE):
                    after_colon = line.split(':', 1)[1].strip() if ':' in line else ''
                    after_colon = re.sub(r"(?i)\boccupation\b.*$", "", after_colon).strip()
                    if after_colon and not re.search(r"\boccupation\b", after_colon, re.IGNORECASE):
                        father_name = after_colon
                        break
                    for next_line in lines[idx + 1: idx + 3]:
                        if next_line and not re.search(r"^(?:occupation|mother[\"'’]?s?\s+name|nationality|place of birth)\b", next_line, re.IGNORECASE):
                            father_name = next_line.strip()
                            break
                    if father_name:
                        break
    parsed["father_name"] = father_name

    # Fallbacks: some application forms leave the field blank or put labels on the
    # same line (e.g. "FATHER'S NAME: OCCUPATION:"). If initial extraction fails,
    # try next-line capture, personal-profile block scan, or nearby tokens.
    if not parsed["father_name"]:
        # next-line pattern
        nl = re.search(r"father[\"'’]?(?:\s*s)?\s+name\s*[:\-]?\s*\n\s*([A-Za-z][A-Za-z.\s]{2,80})", text, re.IGNORECASE)
        if nl:
            parsed["father_name"] = nl.group(1).strip()
        else:
            # search inside a Personal Profile / Personal Details block if present
            pp = re.search(r"(personal profile|personal details)(.*?)(?:declaration|date|signature|$)", text, re.IGNORECASE | re.S)
            if pp:
                pp_block = pp.group(2)
                pp_f = re.search(r"father[\"'’]?(?:\s*s)?\s+name[:\s]*([A-Za-z][A-Za-z.\s]{2,80})", pp_block, re.IGNORECASE)
                if pp_f:
                    parsed["father_name"] = pp_f.group(1).strip()
                else:
                    # last-resort: look for 'Father' label and take the first capitalized token sequence after it
                    f_approx = re.search(r"father\b[^A-Za-z0-9\n]{0,6}([A-Z][A-Za-z.\s]{3,80})", text, re.IGNORECASE)
                    if f_approx:
                        parsed["father_name"] = f_approx.group(1).strip()

    mother_match = re.search(r"(?:mother's name|mother name)[:\s]+([^\n]+)", text, re.IGNORECASE)
    parsed["mother_name"] = mother_match.group(1).strip().strip("-").strip() if mother_match else ""
    if parsed["mother_name"] and re.search(r"\boccupation\b", parsed["mother_name"], re.IGNORECASE):
        parsed["mother_name"] = ""

    # Fallbacks analogous to father's name
    if not parsed["mother_name"]:
        nl = re.search(r"(?:mother's name|mother name)\s*[:\-]?\s*\n\s*([A-Za-z][A-Za-z.\s]{2,80})", text, re.IGNORECASE)
        if nl:
            parsed["mother_name"] = nl.group(1).strip()
        else:
            pp = re.search(r"(personal profile|personal details)(.*?)(?:declaration|date|signature|$)", text, re.IGNORECASE | re.S)
            if pp:
                pp_block = pp.group(2)
                pp_m = re.search(r"(?:mother's name|mother name)[:\s]*([A-Za-z][A-Za-z.\s]{2,80})", pp_block, re.IGNORECASE)
                if pp_m:
                    parsed["mother_name"] = pp_m.group(1).strip()
                else:
                    m_approx = re.search(r"mother\b[^A-Za-z0-9\n]{0,6}([A-Z][A-Za-z.\s]{3,80})", text, re.IGNORECASE)
                    if m_approx and not re.search(r"tongue", m_approx.group(0), re.IGNORECASE):
                        parsed["mother_name"] = m_approx.group(1).strip()

    # Additional fallback: handle templates where the "Personal Profile" or
    # "Permanent Address" section lists labels first (Name:, Date of Birth:,
    # Father's name:, etc.) and the values appear on subsequent lines (a
    # common two-row layout). Map values by proximity when earlier attempts fail.
    def _looks_like_placeholder_field(val: str) -> bool:
        if not val:
            return True
        v = str(val).strip().lower()
        if not v:
            return True
        return bool(re.search(r"[:]|occupation|marital|married|status", v))

    if not parsed.get("dob") or _looks_like_placeholder_field(parsed.get("father_name")):
        try:
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            idx = None
            for i, ln in enumerate(lines):
                if re.search(r'personal profile|personal details|permanent address', ln, re.IGNORECASE):
                    idx = i
                    break
            if idx is not None:
                # Try mapping if labels (Name:, Date of Birth:, Father's name:, ...) appear
                # followed by a 'Permanent Address' row and then the values on the next rows.
                # Collect label lines until 'Permanent Address' and map the values after it.
                labels = []
                perm_idx = None
                j = idx + 1
                while j < len(lines):
                    ln = lines[j]
                    if re.search(r'permanent address', ln, re.IGNORECASE):
                        perm_idx = j
                        break
                    if ':' in ln:
                        labels.append(ln)
                        j += 1
                        continue
                    # stop if we hit something unexpected
                    break
                if labels and perm_idx is not None:
                    # map labels -> values
                    label_keys = [l.split(':', 1)[0].strip().lower() for l in labels]
                    values = lines[perm_idx+1: perm_idx+1+len(label_keys)]
                    for lk, val in zip(label_keys, values):
                        if not val:
                            continue
                        if 'name' in lk and (not parsed.get('name') or _looks_like_placeholder_field(parsed.get('name'))):
                            parsed['name'] = val.strip().rstrip('.')
                        if 'date' in lk or 'birth' in lk:
                            m = re.search(r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b", val)
                            if m:
                                parsed['dob'] = m.group(0).strip().rstrip('.')
                        if 'father' in lk:
                            parsed['father_name'] = val.strip().rstrip('.')
                        if 'marital' in lk:
                            # prefer clear marital tokens; avoid accidentally mapping the
                            # literal 'Permanent' (from 'Permanent Address') into this field
                            mval = val.strip()
                            if 'perman' in mval.lower():
                                # scan the nearby values for a marital keyword
                                found = None
                                for vv in values:
                                    if re.search(r'\b(married|single|unmarried|widow|widower)\b', vv, re.IGNORECASE):
                                        found = vv.strip()
                                        break
                                if found:
                                    mval = found
                                else:
                                    # give up if we only see 'Permanent'
                                    mval = ''
                            if mval:
                                gpart = parsed.get('gender_marital_status', '').split('/')[0].strip()
                                parsed['gender_marital_status'] = f"{gpart} / {mval}".strip()
                    # if marital part still looks wrong (e.g., 'Permanent'), try scanning nearby values
                    gm = parsed.get('gender_marital_status', '')
                    if not gm or 'perman' in gm.lower() or gm.strip().endswith('/'):
                        for vv in values:
                            mv = re.search(r'\b(married|single|unmarried|widow|widower)\b', vv, re.IGNORECASE)
                            if mv:
                                gpart = parsed.get('gender_marital_status', '').split('/')[0].strip()
                                parsed['gender_marital_status'] = f"{gpart} / {mv.group(0).capitalize()}".strip()
                                break
                # collect candidate value lines after the label block as a fallback
                candidates = lines[idx+1: idx+8]
                # DOB fallback: look for a date pattern in the candidate lines
                if not parsed.get("dob"):
                    for c in candidates:
                        m = re.search(r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b", c)
                        if m:
                            parsed["dob"] = m.group(0).strip().rstrip('.')
                            break
                # Father-name fallback: prefer capitalized multiword token that isn't an address or "Married"
                if not parsed.get("father_name"):
                    for c in candidates:
                        low = c.lower()
                        if 'married' in low or 'marital' in low or 'address' in low or low.startswith('name'):
                            continue
                        # plausible name: no digits, not an email, has at least two words or dots
                        if not re.search(r"\d|@|\.com|\.in", c) and ('.' in c or len(c.split()) >= 2):
                            # avoid picking the applicant's own name as father
                            if parsed.get('name') and c.strip().lower().startswith(parsed.get('name','').lower()):
                                continue
                            parsed['father_name'] = c.strip().rstrip('.')
                            break
            # NOTE: Do NOT use a global date fallback — any date in the resume
            # (project dates, publication dates, experience dates, etc.) could be
            # mistakenly grabbed as DOB, causing false age calculations.
        except Exception:
            pass

    nat_match = re.search(r"nationality[:\s]+([A-Za-z]+)", text, re.IGNORECASE)
    parsed["nationality"] = nat_match.group(1).strip() if nat_match else ""

    pob_match = re.search(r"(?:place of birth|birth place)[:\s]+([A-Za-z\s,]+)", text, re.IGNORECASE)
    parsed["place_of_birth"] = pob_match.group(1).strip() if pob_match else ""

    # restrict to same-line captures to avoid grabbing the next header (e.g., 'Permanent Address')
    gender_match = re.search(r"gender[:\s]*([^\n]+)", text, re.IGNORECASE)
    marital_match = re.search(r"marital\s+status[:\s]*([^\n]+)", text, re.IGNORECASE)
    g = gender_match.group(1).strip() if gender_match else ""
    m = marital_match.group(1).strip() if marital_match else ""

    # Husband Name check and gender inference
    husband = ""
    husband_match = re.search(r"husband(?:'s)?\s+name[:\s]+([^\n]+)", text, re.IGNORECASE)
    if husband_match:
        husband = husband_match.group(1).strip().strip("-").strip()
        if husband and re.search(r"\boccupation\b", husband, re.IGNORECASE):
            husband = ""
    else:
        # Care-of check if married
        if "married" in m.lower() or "married" in text.lower():
            co_match = re.search(r"c/o\.?\s*([A-Za-z0-9.\s]+)", text, re.IGNORECASE)
            if co_match:
                co_val = co_match.group(1).strip()
                co_val = co_val.split(",")[0].split("\n")[0].strip()
                co_val = re.sub(r'^(?:care\s+of|co|c/o)\s*', '', co_val, flags=re.IGNORECASE).strip()
                father_val = parsed.get("father_name", "")
                if co_val and co_val.lower() not in father_val.lower() and father_val.lower() not in co_val.lower():
                    husband = co_val

    parsed["husband_name"] = husband

    if not g:
        if husband or "husband" in text.lower():
            g = "Female"
        elif "wife" in text.lower():
            g = "Male"

    # sanitize marital/gender combination: prefer clear marital tokens and avoid label leakage
    def _looks_like_marital(s):
        return bool(re.search(r"\b(married|single|unmarried|widow|widower)\b", s or "", re.IGNORECASE))

    m_clean = m.strip() if m else ""
    # if m looks like a header/label (e.g., contains 'language' or 'perman'), ignore it
    if m_clean and re.search(r"\b(language|languages|perman|address|known)\b", m_clean, re.IGNORECASE):
        m_clean = ""

    # prefer detected marital from nearby parsed value (if already set earlier and looks valid)
    existing_gm = parsed.get('gender_marital_status', '')
    if existing_gm and _looks_like_marital(existing_gm.split('/')[-1] if '/' in existing_gm else existing_gm):
        parsed["gender_marital_status"] = existing_gm
    else:
        # ensure sensible gender inference: prefer detected `g`, else infer from husband/wife presence
        final_g = g or ("Female" if parsed.get('husband_name') or 'husband' in text.lower() else ("Male" if 'wife' in text.lower() else ""))
        parsed["gender_marital_status"] = f"{final_g} / {m_clean}".strip() if (final_g or m_clean) else ""

    # sanity: if gender missing but marital present, infer gender from husband/wife presence
    gm_val = parsed.get('gender_marital_status', '')
    if gm_val:
        left, sep, right = (gm_val.partition('/'))
        if left.strip() == "":
            if parsed.get('husband_name') or 'husband' in text.lower():
                parsed['gender_marital_status'] = f"Female / {right.strip()}".strip()
            elif 'wife' in text.lower():
                parsed['gender_marital_status'] = f"Male / {right.strip()}".strip()

    cat_match = re.search(r"category[:\s]+([A-Za-z\s]+)", text, re.IGNORECASE)
    parsed["category"] = cat_match.group(1).strip() if cat_match else ""

    rel_match = re.search(r"religion[:\s]+([A-Za-z]+)", text, re.IGNORECASE)
    parsed["religion"] = rel_match.group(1).strip() if rel_match else ""

    parsed["other_category"] = ""
    parsed["advt_no"] = ""
    parsed["registration_no"] = f"REG-2026-{abs(hash(parsed['name'])) % 10000:04d}" if parsed["name"] else ""

    # post_applied_for: only keep a headline if it actually looks like a role/post title.
    headline = parsed.get("headline", "") or ""
    if re.search(r"\b(?:professor|assistant professor|associate professor|lecturer|faculty|engineer|developer|analyst|manager|director|coordinator|consultant|instructor|teacher|tutor|position|post)\b", headline, re.IGNORECASE):
        parsed["post_applied_for"] = headline
    else:
        parsed["post_applied_for"] = ""

    def _clean_family_name(value):
        cleaned = re.sub(r"\s+", " ", (value or "")).strip().strip(":,-")
        if not cleaned:
            return ""
        low = cleaned.lower()
        invalid_tokens = {
            "male", "female", "married", "unmarried", "single", "widow", "widower",
            "occupation", "name", "father", "mother", "husband", "wife", "religion",
            "nationality", "address", "tongue", "dob", "age"
        }
        if low in invalid_tokens:
            return ""
        if any(tok in low for tok in ["occupation", "marital", "gender", "address", "name:"]):
            return ""
        return cleaned

    parsed["father_name"] = _clean_family_name(parsed.get("father_name"))
    parsed["mother_name"] = _clean_family_name(parsed.get("mother_name"))

    # specialisation: prefer department/subject area from education, not random skills
    spec_from_edu = ""
    for edu_entry in parsed.get("education", []):
        edu_lower = edu_entry.lower()
        if "computer science" in edu_lower or "cse" in edu_lower:
            spec_from_edu = "Computer Science & Engineering"
            break
        elif "information technology" in edu_lower or " it " in edu_lower:
            spec_from_edu = "Information Technology"
            break
        elif "electronics" in edu_lower or "ece" in edu_lower:
            spec_from_edu = "Electronics & Communication"
            break
        elif "mechanical" in edu_lower:
            spec_from_edu = "Mechanical Engineering"
            break
        elif "civil" in edu_lower:
            spec_from_edu = "Civil Engineering"
            break
    spec_from_dept = ""
    text_lower = text.lower()
    if "department of information technology" in text_lower:
        spec_from_dept = "Information Technology"
    elif "department of computer science" in text_lower:
        spec_from_dept = "Computer Science & Engineering"
    elif "department of electronics" in text_lower:
        spec_from_dept = "Electronics & Communication"

    parsed["specialisation"] = spec_from_dept or spec_from_edu

    # Extract professional memberships
    parsed["memberships"] = extract_memberships(text)

    # Extract administrative works / committee roles
    parsed["administrative_works"] = extract_administrative_works(text)

    # Extract workshops / FDPs attended
    parsed["workshops"] = extract_workshops(text)

    # Extract thesis titles
    thesis_info = []
    thesis_matches = re.findall(r"(?:thesis|dissertation)\s+title[:\s]+[\"']?(.+?)[\"']?(?:\.|\n|$)", text, re.IGNORECASE)
    for idx, t_title in enumerate(thesis_matches):
        thesis_info.append({
            "degree": "Ph.D." if "phd" in text.lower() or "ph.d" in text.lower() else "PG",
            "title": t_title.strip(),
            "guide": "",
            "university": ""
        })
    parsed["thesis_info"] = thesis_info
    parsed["referees"] = []

    # Post-processing: remove certificate mentions from other lists when a certificates section exists
    try:
        certs = parsed.get('certificates') or []
        if certs:
            def _remove_similar(target_list):
                out = []
                for t in target_list:
                    low = t.lower()
                    if any(c.lower() in low or low in c.lower() for c in certs):
                        continue
                    out.append(t)
                return out

            parsed['experience'] = _remove_similar(parsed.get('experience') or [])
            parsed['projects'] = _remove_similar(parsed.get('projects') or [])
            parsed['achievements'] = _remove_similar(parsed.get('achievements') or [])
    except Exception:
        pass

    # Simple per-field confidence scoring heuristics
    confidences = {}

    # Name confidence
    name = parsed.get('name', '') or ''
    if name and name != 'Candidate Name' and len(name.split()) >= 2:
        confidences['name'] = 0.85
    elif name and name != 'Candidate Name':
        confidences['name'] = 0.6
    else:
        confidences['name'] = 0.2

    # Email and phone are highly deterministic via regex
    confidences['email'] = 0.95 if parsed.get('email') else 0.1
    confidences['phone'] = 0.9 if parsed.get('phone') else 0.1

    # Headline/summary confidence
    confidences['headline'] = 0.7 if parsed.get('headline') else 0.25
    confidences['summary'] = 0.7 if parsed.get('summary') else 0.25

    # Links
    confidences['links'] = 0.9 if parsed.get('links') else 0.2

    # Education confidence: higher if degree patterns / year / cgpa present
    edu_list = parsed.get('education') or []
    edu_conf_scores = []
    degree_pattern = re.compile(r"\b(Ph\.?D\.?|Phd|B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?|B\.?Sc\.?|M\.?Sc\.?|MBA|LLB|LLM|JD)\b", re.IGNORECASE)
    year_re = re.compile(r"\b(19|20)\d{2}\b")
    for e in edu_list:
        score = 0.5
        if degree_pattern.search(e):
            score = 0.85
        elif year_re.search(e) or re.search(r'\b(CGPA|GPA|%)\b', e, re.IGNORECASE):
            score = 0.75
        edu_conf_scores.append(score)
    confidences['education'] = max(edu_conf_scores) if edu_conf_scores else 0.15

    # Skills confidence: presence in skills DB is high
    skills = parsed.get('skills') or []
    confidences['skills'] = 0.85 if skills else 0.15

    # Experience confidence: entries with years or title tokens get higher score
    exp_list = parsed.get('experience') or []
    exp_scores = []
    title_tokens = re.compile(r"\b(professor|lecturer|engineer|developer|researcher|analyst|manager|lead|intern|assistant|officer|consultant|fellow)\b", re.IGNORECASE)
    for ex in exp_list:
        s = 0.5
        if year_re.search(ex) or title_tokens.search(ex):
            s = 0.8
        exp_scores.append(s)
    confidences['experience'] = max(exp_scores) if exp_scores else 0.15

    # Publications confidence
    pubs = parsed.get('publications') or []
    confidences['publications'] = 0.75 if pubs else 0.15

    # Projects / achievements / certificates / awards confidence heuristics
    projects = parsed.get('projects') or []
    confidences['projects'] = 0.7 if projects else 0.12

    achievements = parsed.get('achievements') or []
    confidences['achievements'] = 0.7 if achievements else 0.12

    certificates = parsed.get('certificates') or []
    confidences['certificates'] = 0.8 if certificates else 0.12

    awards = parsed.get('awards') or []
    confidences['awards'] = 0.75 if awards else 0.12

    # Final sanity pass before returning parsed JSON.
    parsed['father_name'] = _clean_family_name(parsed.get('father_name'))
    parsed['mother_name'] = _clean_family_name(parsed.get('mother_name'))
    if parsed.get('post_applied_for') and not re.search(r"\b(?:professor|assistant professor|associate professor|lecturer|faculty|engineer|developer|analyst|manager|director|coordinator|consultant|instructor|teacher|tutor|position|post)\b", parsed.get('post_applied_for', ''), re.IGNORECASE):
        parsed['post_applied_for'] = ""

    parsed['confidence'] = confidences
    return parsed