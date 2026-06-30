import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Custom canvas to generate dynamic 'Page X of Y' page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1F2937"))
        
        # Header (Top of every page)
        self.drawString(54, 755, "APPLICATION FORM FOR FACULTY POSITION - JK LAKSHMIPAT UNIVERSITY")
        self.setStrokeColor(colors.HexColor("#000000"))
        self.setLineWidth(1)
        self.line(54, 747, 558, 747)
        
        # Footer (Bottom of every page)
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Confidential Candidate Screening Document")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_text)
        
        self.restoreState()

def draw_form_frame(c: canvas.Canvas, doc: SimpleDocTemplate):
    """
    Draws a simple outer border around the content area to mimic
    the official form look (like the reference images).
    """
    c.saveState()
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, stroke=1, fill=0)
    c.restoreState()

def fit_cell(text, style, max_width, max_height):
    """
    Prevent long resume text from overlapping other rows/cells.
    Shrinks content to fit inside a fixed-height table cell.
    """
    safe = "" if text is None else str(text)
    para = Paragraph(safe.replace("\n", "<br/>"), style)
    # shrink is a last resort; if the row height is sufficient, text stays normal size.
    return KeepInFrame(max_width, max_height, [para], mode="shrink")


def parse_education_entry(edu_str):
    """Helper to extract education qualification details from a raw string.
    
    Designed to handle ALL common resume education formats:
    - "Degree | Institution | Year | Score"
    - "Institution, Location | Month Year | Degree Subject"
    - "Degree in Subject, Institution, Year, Score"
    - "Degree from Institution Year Score"
    - "Bachelor/Master of Science: Subject | University | Year"
    - OCR-garbled variants of the above
    """
    if not edu_str:
        return {
            "degree": "", "other_degree": "", "spec": "", "inst": "", "univ": "",
            "year": "", "percent": "", "cgpa": "", "division": ""
        }
        
    degree = ""
    other_degree = ""
    spec = ""
    inst = ""
    univ = ""
    year = ""
    percent = ""
    cgpa = ""
    division = ""
    
    edu_lower = edu_str.lower()
    
    # ── 1. Detect Degree ──────────────────────────────────────────────────────
    # ORDER MATTERS: check more specific patterns first, then broader ones.
    # Check 12th/HSC BEFORE SSC/10th since "class xii" contains "class x".
    
    if "ph.d" in edu_lower or "phd" in edu_lower or "phld" in edu_lower or "doctor of philosophy" in edu_lower:
        degree = "Ph.D."
    elif re.search(r'\bm\.?phil\.?\b', edu_lower):
        degree = "M.Phil."
    elif "m.tech" in edu_lower or "mtech" in edu_lower or "master of technology" in edu_lower:
        degree = "M.Tech."
    elif re.search(r'\bm\.?sc\.?\b', edu_lower) or "master of science" in edu_lower:
        degree = "M.Sc."
        other_degree = "PG"
    elif "b.tech" in edu_lower or "btech" in edu_lower or ("b.e" in edu_lower and "b.e./" not in edu_lower) or "bachelor of engineering" in edu_lower or "bachelor of technology" in edu_lower:
        degree = "B.E. / B.Tech"
    elif re.search(r'\bb\.?sc\.?\b', edu_lower) or "bachelor of science" in edu_lower:
        degree = "B.Sc."
        other_degree = "UG"
    elif re.search(r'\bmca\b', edu_lower):
        degree = "MCA"
        other_degree = "MCA"
    elif re.search(r'\bbca\b', edu_lower):
        degree = "BCA"
        other_degree = "BCA"
    elif "diploma" in edu_lower:
        degree = "Diploma"
        other_degree = "Diploma"
    # 12th / HSC / Class XII / 10+2 — MUST be checked BEFORE SSC/10th
    elif re.search(r'\bhsc\b', edu_lower) or "intermediate" in edu_lower or "12th" in edu_lower or re.search(r'\bclass\s*xii\b', edu_lower) or re.search(r'\b10\s*\+\s*2\b', edu_lower):
        degree = "HSC / Intermediate"
        other_degree = "12th"
    elif re.search(r'\bs\.?s\.?c\.?\b', edu_lower) or "secondary" in edu_lower or "10th" in edu_lower or re.search(r'\bclass\s*x\b', edu_lower):
        degree = "S.S.C."
        other_degree = "10th"
    elif re.search(r'\b(mba)\b', edu_lower):
        degree = "MBA"
        other_degree = "PG"
    elif re.search(r'\bllm\b', edu_lower):
        degree = "LLM"
        other_degree = "PG"
    elif re.search(r'\bllb\b', edu_lower):
        degree = "LLB"
        other_degree = "UG"
    elif re.search(r'\bbba\b', edu_lower):
        degree = "BBA"
        other_degree = "UG"
    elif re.search(r'\bb\.?com\b', edu_lower):
        degree = "B.Com."
        other_degree = "UG"
    elif re.search(r'(?:\b|\s)m\.?com\b', edu_lower):
        degree = "M.Com."
        other_degree = "PG"
    elif re.search(r'(?:\b|\s)m\.?a\.?(?:\s|$|\|)', edu_lower):
        degree = "M.A."
        other_degree = "PG"
    elif re.search(r'(?:\b|\s)b\.?a\.?(?:\s|$|\|)', edu_lower):
        degree = "B.A."
        other_degree = "UG"
    elif re.search(r'\bmaster\b', edu_lower):
        degree = "Master's"
        other_degree = "PG"
    elif re.search(r'\bbachelor\b', edu_lower):
        degree = "Bachelor's"
        other_degree = "UG"
    elif re.search(r'\bassociate\b', edu_lower):
        degree = "Associate"
        other_degree = "UG"
    
    # For Master/Bachelor: try to refine the degree string from the actual text
    if degree in ("Master's", "Bachelor's"):
        for part in edu_str.split("|"):
            part_clean = part.strip()
            if degree == "Master's":
                m_deg = re.search(r'\b(Master of [A-Za-z]+|Masters? in [A-Za-z]+)\b', part_clean, re.IGNORECASE)
            else:
                m_deg = re.search(r'\b(Bachelor of [A-Za-z]+|Bachelors? in [A-Za-z]+)\b', part_clean, re.IGNORECASE)
            if m_deg:
                found_deg = m_deg.group(0).strip()
                if len(found_deg) < 40 and not any(k in found_deg.lower() for k in ["university", "college", "institute"]):
                    degree = found_deg
                break
    
    # For M.Sc./B.Sc./M.A./B.A.: try to refine the degree string from a pipe-segment containing it
    if degree in ("M.Sc.", "B.Sc.", "M.A.", "B.A.", "M.Com.", "B.Com."):
        deg_abbr = degree.replace(".", "").lower()  # e.g. "msc"
        for part in edu_str.split("|"):
            part_clean = part.strip()
            if re.search(r'\b' + re.escape(deg_abbr[:2]) + r'\.?' + re.escape(deg_abbr[2:]) + r'\.?\b', part_clean, re.IGNORECASE):
                # Found the segment with the degree; check if there's a subject after it
                # But DON'T expand the degree string — keep it short (e.g., "M.Sc.")
                break

    # ── 2. Year Match ─────────────────────────────────────────────────────────
    all_years = re.findall(r"\b(?:19|20)\d{2}\b", edu_str)
    if all_years:
        year = all_years[-1]
    else:
        month_year = re.search(
            r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[\s,.-]*((?:19|20)\d{2})\b",
            edu_str,
            re.IGNORECASE,
        )
        if month_year:
            year = month_year.group(1)
        
    # ── 3. CGPA / Percent Match ───────────────────────────────────────────────
    cgpa_match = re.search(r"\b(?:cgpa|gpa)[:\s]*([0-9.]+)", edu_str, re.IGNORECASE)
    if not cgpa_match:
        cgpa_match = re.search(r"\b([0-9.]+)\s*/\s*10\b", edu_str)
    percent_match = re.search(r"\b([0-9.]+)\s*%", edu_str, re.IGNORECASE)
    if not percent_match:
        percent_match = re.search(r"\bmarks[:\s]*([0-9.]+)", edu_str, re.IGNORECASE)
    if not percent_match:
        percent_match = re.search(r"(?:distinction|first class|1st class|second class|2nd class)\s+(?:with\s+)?([0-9.]+)\s*%", edu_str, re.IGNORECASE)
        
    if cgpa_match:
        cgpa = cgpa_match.group(1)
    if percent_match:
        percent = percent_match.group(1)
        
    # Prioritize explicit division keywords in the text
    if "distinction" in edu_lower:
        division = "Distinction"
    elif "first class" in edu_lower or "1st class" in edu_lower or re.search(r'\bfirst\b|\b1st\b', edu_lower):
        division = "First"
    elif "second class" in edu_lower or "2nd class" in edu_lower or re.search(r'\bsecond\b|\b2nd\b', edu_lower):
        division = "Second"
    elif "third class" in edu_lower or "3rd class" in edu_lower or re.search(r'\bthird\b|\b3rd\b|\bpass\b', edu_lower):
        division = "Third"
    else:
        division = ""


    # ── 4. Specialisation / Branch extraction ─────────────────────────────────
    # 4a. Parenthetical spec like "Ph.D(CSE)" or "M.Tech(CSE)"
    paren_spec = re.search(r'(?:ph\.?d|m\.?tech|b\.?tech|b\.?e|mca|bca)\s*\(([^)]+)\)', edu_str, re.IGNORECASE)
    if paren_spec:
        raw_spec = paren_spec.group(1).strip()
        spec_map = {
            "cse": "Computer Science & Engineering",
            "cs": "Computer Science",
            "ece": "Electronics & Communication",
            "eee": "Electrical & Electronics",
            "it": "Information Technology",
            "me": "Mechanical Engineering",
            "ce": "Civil Engineering",
        }
        spec = spec_map.get(raw_spec.lower(), raw_spec)
    
    # 4b. "Degree in Subject" pattern — but NOT "in" that's part of institution names
    if not spec:
        # Match "in <Subject>" but not "in <Institution keyword>"
        m_in = re.search(r'\b(?:in|of)\s+([A-Z][A-Za-z&\s]+?)(?:\s*[,|]|\s+(?:from|at|with)\b|\s*$)', edu_str)
        if m_in:
            spec_cand = m_in.group(1).strip()
            spec_cand = re.sub(r'\b(?:19|20)\d{2}\b', '', spec_cand).strip()
            spec_cand = re.sub(r'\b(?:cgpa|gpa|marks|%)\b.*', '', spec_cand, flags=re.IGNORECASE).strip()
            # Don't use if it looks like an institution or a generic degree word
            if spec_cand and len(spec_cand) > 1 and not any(w in spec_cand.lower() for w in [
                "college", "institute", "university", "school", "board", "polytechnic",
                "iit", "iim", "nit", "bits", "iisc"
            ]) and spec_cand.lower() not in [
                "science", "engineering", "technology", "arts", "commerce", 
                "philosophy", "business administration", "computer applications"
            ]:
                spec = spec_cand
    
    # 4c. "Degree : Subject" or "Degree: Subject" pattern (e.g., "Master of Science: Healthcare")
    if not spec:
        m_colon = re.search(r'(?:master|bachelor|associate|doctor)\s+of\s+[a-z]+\s*:\s*([A-Za-z&\s]+?)(?:\s*[,|]|\s*$)', edu_str, re.IGNORECASE)
        if m_colon:
            spec_cand = m_colon.group(1).strip()
            if spec_cand and not any(w in spec_cand.lower() for w in ["college", "institute", "university", "school", "board"]):
                spec = spec_cand
            
    # 4d. Keyword-based fallback — use WORD BOUNDARY matching to avoid false positives
    # e.g., "intermediate" should NOT match "me" → Mechanical Engineering
    if not spec:
        if "computer science" in edu_lower or re.search(r'\bcse\b', edu_lower):
            spec = "Computer Science & Engineering"
        elif "information technology" in edu_lower:
            spec = "Information Technology"
        elif re.search(r'\bmca\b', edu_lower) or re.search(r'\bbca\b', edu_lower):
            spec = "Computer Applications"
        elif "electronics" in edu_lower or re.search(r'\bece\b', edu_lower):
            spec = "Electronics & Communication"
        elif "mechanical engineering" in edu_lower:
            spec = "Mechanical Engineering"
        elif "civil engineering" in edu_lower:
            spec = "Civil Engineering"
        elif "electrical" in edu_lower:
            spec = "Electrical Engineering"

    # 4e. Try extracting subject word(s) immediately after the degree abbreviation
    if not spec:
        # Build a regex from the detected degree
        deg_for_regex = degree.replace(".", "\\.?").replace(" ", "\\s+")
        if deg_for_regex and len(deg_for_regex) >= 2:
            m_after = re.search(r'(?i)(?:\b|\s)' + deg_for_regex + r'\.?\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,2})', edu_str)
            if m_after:
                cand = m_after.group(1).split('|')[0].split(',')[0].strip()
                # Remove trailing prepositions or conjunctions
                cand = re.sub(r'\s+(?:from|at|in|with|and|or)\s*$', '', cand, flags=re.IGNORECASE).strip()
                if cand and len(cand) > 1 and not any(w in cand.lower() for w in [
                    "university", "college", "institute", "school", "board", "year", 
                    "cgpa", "gpa", "marks", "from", "the", "and", "polytechnic"
                ]) and cand.lower() not in [
                    "science", "engineering", "technology", "arts", "commerce", "philosophy"
                ]:
                    spec = cand

    if degree in ("HSC / Intermediate", "S.S.C."):
        # SSC/HSC don't have a branch/specialisation — keep spec blank.
        # (The "10th"/"12th" label goes in the other_degree column, not spec.)
        spec = ""

    # ── 5. Institution and University Extraction ──────────────────────────────
    inst_keywords = ["institute", "college", "school", "academy", "vidyapeeth", "vidyalaya", "bhavan", "mandir", "campus", "polytechnic"]
    univ_keywords = ["university", "univ\\."]
    
    # Well-known acronym institutions that don't contain "university"/"college"/"institute" 
    known_acronyms = {
        "iit": "IIT", "iim": "IIM", "nit": "NIT", "bits": "BITS", "iisc": "IISc",
        "ignou": "IGNOU", "jntu": "JNTU", "jklu": "JKLU", "vtu": "VTU",
        "isro": "ISRO", "drdo": "DRDO",
    }
    
    def _find_org_names(text, keywords):
        """Find organization names containing the given keywords in the text."""
        results = []
        for kw in keywords:
            pattern = r'(?:[A-Z][A-Za-z.\'\-]*\s+)*(?:[A-Z][A-Za-z.\'\-]*\s+)?(?:' + kw + r')(?:\s+(?:of|for|and|&)\s+[A-Za-z.\'\-]+(?:\s+[A-Za-z.\'\-]+)*)?(?:,\s*[A-Z][A-Za-z.\'\-]+(?:[ \-][A-Z][A-Za-z.\'\-]+)*)?'
            for m in re.finditer(pattern, text, re.IGNORECASE):
                name = m.group(0).strip()
                name = re.sub(r'\b(?:Ph\.?D|M\.?Tech|B\.?Tech|B\.?E|MCA|BCA|Diploma|S\.?S\.?C)\b\.?\s*(?:\([^)]*\))?\s*', '', name, flags=re.IGNORECASE).strip()
                name = re.sub(r'\b(?:19|20)\d{2}\b', '', name).strip()
                name = re.sub(r'\s+', ' ', name).strip().strip(",").strip(".")
                if name and len(name) > 3:
                    results.append(name)
        return results
    
    found_insts = _find_org_names(edu_str, inst_keywords)
    found_univs = _find_org_names(edu_str, univ_keywords)
    
    # Try segment-based approach as fallback
    raw_segs = [s.strip() for s in edu_str.split("|")]
    if len(raw_segs) == 1 and "," in raw_segs[0]:
        raw_segs = [s.strip() for s in raw_segs[0].split(",")]
    
    ignored_org_words = {"ssc", "hsc", "cbse", "icse", "intermediate", "10th", "12th", "phd", "ph.d", "mtech", "m.tech", "btech", "b.tech", "mca", "bca", "mba", "bba", "bsc", "b.sc", "msc", "m.sc", "be", "b.e", "me", "m.e"}
    for seg in raw_segs:
        seg_lower = seg.lower().strip()
        seg_clean = seg.strip()
        if re.match(r'^\s*(?:19|20)\d{2}\s*$', seg_clean):
            continue
        if any(w in seg_lower for w in ["cgpa", "gpa", "%", "marks", "distinction", "1st class", "first class", "year of passing"]):
            continue
        seg_norm = seg_clean.replace(".", "").replace(" ", "").lower()
        if seg_norm in ignored_org_words:
            continue
        if "university" in seg_lower or "univ" in seg_lower:
            if seg_clean not in found_univs:
                found_univs.append(seg_clean)
        elif "board" in seg_lower:
            if seg_clean not in found_univs:
                found_univs.append(seg_clean)
        elif re.fullmatch(r"[A-Z]{3,12}(?:\s*[A-Z]{2,12})?", seg_clean.replace(".", "").replace(",", "").strip()):
            if seg_clean not in found_univs:
                found_univs.append(seg_clean)
        elif re.match(r"^[A-Z]{2,10},[A-Za-z]+$", seg_clean.replace(" ", "")):
            if seg_clean not in found_univs:
                found_univs.append(seg_clean)
        elif any(ok in seg_lower for ok in inst_keywords):
            if seg_clean not in found_insts:
                found_insts.append(seg_clean)
    
    # 5b. Check for known acronyms in the text (IIT, IIM, IGNOU, etc.)
    for acronym_lower, acronym_display in known_acronyms.items():
        if re.search(r'\b' + re.escape(acronym_lower) + r'\b', edu_lower):
            # Try to grab the full name like "IIT Madras" or "IIM Bangalore"
            m_acr = re.search(r'\b(' + re.escape(acronym_display) + r'(?:\s+[A-Z][a-zA-Z]+)?)\b', edu_str)
            if m_acr:
                acr_name = m_acr.group(1).strip()
                if acr_name not in found_insts and acr_name not in found_univs:
                    found_insts.append(acr_name)
    
    # 5c. Check for "Government <keyword>" pattern  
    m_govt = re.search(r'\b(Government\s+[A-Za-z]+(?:\s+[A-Za-z]+)?(?:,\s*[A-Z][a-zA-Z]+)?)\b', edu_str)
    if m_govt:
        govt_name = m_govt.group(1).strip()
        if govt_name not in found_insts:
            found_insts.append(govt_name)
    
    # 5d. Check for "from <Institution>" pattern
    if not found_insts and not found_univs:
        m_from = re.search(r'\bfrom\s+([A-Z][A-Za-z\s.]+?)(?:\s*[,|]|\s+\d{4}|\s*$)', edu_str)
        if m_from:
            from_name = m_from.group(1).strip()
            if len(from_name) > 3:
                found_insts.append(from_name)
    
    def clean_name(name_str):
        if not name_str:
            return ""
        name_str = re.sub(r'^(?:ph\.?d\.?|m\.?tech\.?|b\.?tech\.?|b\.?e\.?|master\'s|bachelor\'s|m\.?sc\.?|mba|llb|llm|bba|mca|bca|diploma)\s*(?:\([^)]*\))?\s*(?:in|of)?\s*', '', name_str, flags=re.IGNORECASE)
        name_str = re.sub(r'\b(?:19|20)\d{2}\b', '', name_str)
        name_str = re.sub(r'\b(?:cgpa|gpa|marks|%|distinction|1st class|first class)\b.*', '', name_str, flags=re.IGNORECASE)
        name_str = re.sub(r'\s+', ' ', name_str)
        name_str = name_str.strip().strip("-").strip("|").strip(",").strip(".").strip()
        return name_str

    inst = ""
    for cand in found_insts:
        cleaned = clean_name(cand)
        if cleaned:
            inst = cleaned
            break
            
    univ = ""
    for cand in found_univs:
        cleaned = clean_name(cand)
        if cleaned:
            univ = cleaned
            break
    
    # If we only found one type, try to differentiate
    if inst and not univ:
        if "university" in inst.lower():
            univ = inst
            inst = ""
    if univ and not inst:
        inst = univ
            


    if inst == "JKLU" and "jklu" not in edu_lower:
        inst = ""
    if univ == "JKLU" and "jklu" not in edu_lower:
        univ = ""

    # ── 6. Degree refinement (generic → specific) ────────────────────────────
    if degree == "Bachelor's":
        if "computer" in edu_lower or "tech" in edu_lower or "engineering" in edu_lower:
            degree = "B.Tech"
        elif "law" in edu_lower or "llb" in edu_lower:
            degree = "BBA LLB"
        elif "business" in edu_lower or "management" in edu_lower or "bba" in edu_lower:
            degree = "BBA"
        elif "science" in edu_lower or "bsc" in edu_lower:
            degree = "B.Sc."
        else:
            degree = "B.A."
            
    if degree == "Master's":
        if "computer" in edu_lower or "tech" in edu_lower or "engineering" in edu_lower:
            degree = "M.Tech"
        elif "business" in edu_lower or "management" in edu_lower or "mba" in edu_lower:
            degree = "MBA"
        elif "science" in edu_lower or "msc" in edu_lower:
            degree = "M.Sc."
        else:
            degree = "M.A."

    # ── 7. Remove spec from the "from Institution" false positive ─────────────
    if spec:
        spec_lower = spec.lower()
        # If spec accidentally captured an institution name, clear it
        if any(w in spec_lower for w in ["university", "college", "institute", "school", "board", "polytechnic", "iit", "iim", "nit"]):
            spec = ""
        # If spec starts with "from " or "at ", clean it
        spec = re.sub(r'^(?:from|at|on)\s+', '', spec, flags=re.IGNORECASE).strip()
    
    if not inst and not univ:
        inst = "University"
        univ = "University"

    return {
        "degree": degree,
        "other_degree": other_degree,
        "spec": spec,
        "inst": inst,
        "univ": univ,
        "year": year,
        "percent": percent,
        "cgpa": cgpa,
        "division": division
    }


def parse_experience_entry(exp_str):
    """Helper to parse experience details from a raw string."""
    if not exp_str:
        return {
            "org": "", "desig": "", "post_phd": "No", "doj": "", "dol": "",
            "years": "", "months": "0", "pay": "N/A"
        }
        
    desig = ""
    org = ""
    doj = ""
    dol = ""
    exp_years = "0"
    exp_months = "0"
    pay = "N/A"
    
    exp_lower = exp_str.lower()
    
    # 1. Extract Designation
    desig_pattern = re.compile(
        r'\b(?:senior|sr\.?|assistant|asst\.?|associate|adjunct|visiting|teaching|research|software|lead|principal|head)\s*'
        r'(?:assistant|asst\.?|associate|software|research|project)?\s*'
        r'(?:professor|lecturer|teacher|fellow|scientist|engineer|developer|analyst|manager|lead|officer|intern|consultant|coordinator|proctor|tutor|instructor)\b',
        re.IGNORECASE
    )
    m_desig = desig_pattern.search(exp_str)
    if m_desig:
        desig = m_desig.group(0).strip()
    else:
        desig_keywords = ["professor", "lecturer", "teacher", "fellow", "researcher", "scientist", "engineer", "developer", "instructor", "assistant", "analyst", "manager", "lead", "officer", "intern", "tutor", "consultant", "coordinator", "participant", "member", "executive"]
        for dk in desig_keywords:
            m = re.search(r'\b(' + dk + r')\b', exp_lower)
            if m:
                desig = m.group(1)
                break
                
    if desig:
        desig = desig.strip().title()
        desig = desig.replace("Sr.", "Senior ").replace("Asst.", "Assistant ").replace("Asst ", "Assistant ")
        desig = re.sub(r'\s+', ' ', desig).strip()
        
    # 2. Extract Organization - Robust approach
    org_keywords = ["university", "college", "institute", "school", "technologies", "solutions", "services", "systems", "labs", "ltd", "limited", "pvt", "inc", "co.", "corporation", "corp", "group", "associate", "associates", "club", "academy", "hospital", "bank", "firm", "centre", "center"]
    
    def extract_org_name(text):
        for kw in org_keywords:
            # Look for the keyword and capture words around it
            kw_safe = re.escape(kw)
            pattern = r'(?:[A-Z][A-Za-z.\'\-]*\s+)*(?:[A-Z][A-Za-z.\'\-]*\s+)?(?:\b' + kw_safe + r'\b)(?:\s+(?:of|for|and|&)\s+[A-Za-z.\'\-]+(?:\s+[A-Za-z.\'\-]+)*)?'
            for m in re.finditer(pattern, text, re.IGNORECASE):
                cand = m.group(0).strip()
                # Clean up extracted candidate
                cand = re.sub(r'^(?:in|at|for|with)\s+', '', cand, flags=re.IGNORECASE)
                cand = re.sub(r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4}\b|\b\d{4}\b', '', cand, flags=re.IGNORECASE)
                cand = re.sub(r'\b(?:to|present|current|\-|\–)\b', '', cand, flags=re.IGNORECASE).strip()
                # Discard if it's too short or just the keyword
                if cand.lower() != kw and len(cand) > 5:
                     return cand
        return ""
        
    org = extract_org_name(exp_str)
                
    def is_acronym(s):
        s2 = s.replace(".", "").strip()
        return bool(re.fullmatch(r"[A-Z]{3,12}(?:\s*[A-Z]{2,12})?", s2))

    if not org:
        m_org = re.search(r'\b(?:in|at|for|with)\s+([^,.\n|]+)', exp_str, re.IGNORECASE)
        if m_org:
            cand = m_org.group(1).strip()
            if any(ok in cand.lower() for ok in org_keywords) or is_acronym(cand):
                org = cand

    if not org and "|" in exp_str:
        for p in exp_str.split("|"):
            p_clean = p.strip()
            if not p_clean: continue
            # Avoid picking a segment that's just the designation or just dates
            if desig and desig.lower() == p_clean.lower(): continue
            if re.search(r'\b(19|20)\d{2}\b', p_clean): continue
            
            if any(kw in p_clean.lower() for kw in org_keywords) or is_acronym(p_clean):
                org = p_clean
                break
                
    if org:
        if desig and desig.lower() in org.lower() and len(org.lower().replace(desig.lower(), "").strip()) > 3:
            org = org.replace(desig, "").replace(desig.upper(), "").replace(desig.lower(), "")

    # 3. Smart Fallback using pipe and comma splitting for unassigned parts
    if not desig or not org:
        # Strip dates and descriptions to find remaining text
        date_pattern = re.compile(
            r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*\d{4}\s*[-–to]+\s*(?:present|current|\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*\d{4})\b'
            r'|\b\d{4}\s*[-–to]+\s*(?:present|current|\d{4})\b'
            r'|\b\d{1,2}/\d{2,4}\s*[-–to]+\s*(?:present|current|\d{1,2}/\d{2,4})\b',
            re.IGNORECASE
        )
        exp_clean = exp_str
        for m in date_pattern.finditer(exp_clean):
            exp_clean = exp_clean.replace(m.group(0), " | ")
        exp_clean = re.sub(r'[-+*•]\s+.*$', ' | ', exp_clean) # Remove bullet descriptions
        
        split_char = "|" if "|" in exp_clean else ","
        parts = []
        for p in exp_clean.split(split_char):
            p = p.strip("-,.() \t")
            if not p or len(p) < 3 or re.match(r'^\d+$', p): continue
            if date_pattern.search(p) or any(x in p.lower() for x in ["present", "current", "ongoing"]): continue
            if desig and desig.lower() in p.lower(): continue
            if org and org.lower() in p.lower(): continue
            parts.append(p)
            
        if parts:
            if not desig and not org:
                if len(parts) >= 2:
                    if len(parts[0]) <= 40:
                        desig, org = parts[0], parts[1]
                    else:
                        org, desig = parts[0], parts[1]
                else:
                    p = parts[0]
                    if len(p) <= 35 and any(k in p.lower() for k in ["professor", "lecturer", "teacher", "fellow", "researcher", "scientist", "engineer", "developer", "instructor", "assistant", "analyst", "manager", "lead", "officer", "intern", "tutor", "consultant", "coordinator", "participant", "member", "executive", "worker", "driver", "clerk", "associate", "technician", "specialist"]):
                        desig = p
                    else:
                        org = p
            elif not desig:
                desig = parts[0]
            elif not org:
                org = parts[0]
                
    if desig: desig = desig.strip("-,.() ").title()
    if org: org = org.strip("-,.() ")
    
    # Fallback if STILL empty to avoid errors
    if not desig and org: desig = "Member/Associate"
    if not org and desig: org = "Independent/Freelance"
    if not org and not desig:
        desig = "Participant"
        org = "Organization"

    org = re.sub(r'\s+', ' ', org).strip().strip("-").strip(",").strip()
        
    # 3. Extract Dates & Calculate Duration
    date_pattern = r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4}\b|\b\d{4}\b'
    date_matches = re.findall(date_pattern, exp_str, re.IGNORECASE)
    
    # Check present/current status in the dates segment of the experience string to avoid matching substrings (e.g. "presented") in job descriptions
    date_seg = ""
    if "|" in exp_str:
        for p in exp_str.split("|"):
            if re.search(r'\b(?:19|20)\d{2}\b', p):
                date_seg = p
                break
    if not date_seg:
        date_seg = re.split(r'[-+*•«]', exp_str)[0]
    is_present = bool(re.search(r'\b(?:present|current|till\s+date|ongoing|now|working)\b', date_seg.lower()))

    
    if len(date_matches) >= 2:
        doj = date_matches[0].title()
        dol = "Present" if is_present else date_matches[1].title()
    elif len(date_matches) == 1:
        doj = date_matches[0].title()
        dol = "Present" if is_present else ""
    else:
        years = re.findall(r"\b(?:19|20)\d{2}\b", exp_str)
        if len(years) >= 2:
            doj = f"July {years[0]}"
            dol = "Present" if is_present else f"June {years[1]}"
        elif len(years) == 1:
            doj = f"July {years[0]}"
            dol = "Present" if is_present else ""
            
    years_list = re.findall(r"\b(?:19|20)\d{2}\b", exp_str)
    if years_list:
        try:
            y1 = int(years_list[0])
            y2 = 2026 if dol.lower() == "present" else (int(years_list[1]) if len(years_list) >= 2 else y1)
            diff = max(0, y2 - y1)
            exp_years = str(diff) if diff > 0 else "0"
        except:
            exp_years = "0"
            
    if not exp_years or exp_years == "0":
        exp_years = "1"
        
    if org == "Institution" and "institution" not in exp_lower:
        org = ""
        
    return {
        "org": org,
        "desig": desig,
        "post_phd": "No",
        "doj": doj,
        "dol": dol,
        "years": exp_years,
        "months": exp_months,
        "pay": pay
    }


def parse_publication_details(pub_str):
    """Helper to extract title, journal, type, and year from a publication string."""
    title = pub_str
    journal = ""
    pub_type = "Conference"
    year = ""
    
    year_match = re.search(r"\b((?:19|20)\d{2})\b", pub_str)
    if year_match:
        year = year_match.group(1)
        
    quote_match = re.search(r'["\']([^"\']{10,})["\']', pub_str)
    if quote_match:
        title = quote_match.group(1).strip()
        post_quote = pub_str[quote_match.end():].strip()
        in_match = re.search(r'(?:\bin\s+|,\s*)([A-Za-z0-9\s&()\-:]+)', post_quote, re.IGNORECASE)
        if in_match:
            journal = in_match.group(1).strip()
    else:
        parts = pub_str.split(",")
        if len(parts) > 0:
            title = parts[0].strip()
        if len(parts) > 1:
            journal = parts[1].strip()
            
    if journal:
        journal = re.split(r'\b(?:held|vol|issue|pp|\d{4}|issn)\b', journal, flags=re.IGNORECASE)[0].strip()
        journal = journal.strip(",").strip("-").strip()
        
    pub_lower = pub_str.lower()
    if any(k in pub_lower for k in ["journal", "transactions", "ijrece", "computations"]):
        pub_type = "Journal"
    else:
        pub_type = "Conference"
        
    # Check SCI - Use word boundary
    is_sci = bool(re.search(r'\bsci\b', pub_lower))
        
    return {
        "title": title,
        "journal": journal,
        "type": pub_type,
        "year": year,
        "is_sci": "SCI" if is_sci else "Non-SCI"
    }


def generate_candidate_pdf(candidate_data, output_path):
    """
    Generate a highly structured official ReportLab PDF that mirrors 
    the institutional 'APPLICATION FORM FOR FACULTY POSITION' tables.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Page setup:
    # - Use A4 to match typical institutional form dimensions in India.
    # - Keep margins modest so the grid fills the page like the sample.
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24
    )
    
    styles = getSampleStyleSheet()

    # helper: normalize Unicode punctuation that can trigger PDF font fallbacks
    def _norm(s):
        if not s:
            return ""
        ns = str(s)
        # common replacements: smart quotes, long dashes, ellipsis, non-breaking spaces
        ns = ns.replace('\u201c', '"').replace('\u201d', '"')
        ns = ns.replace('\u2018', "'").replace('\u2019', "'")
        ns = ns.replace('\u2013', '-').replace('\u2014', '-')
        ns = ns.replace('\u2026', '...')
        ns = ns.replace('\xa0', ' ')
        # normalize fancy punctuation often introduced by MS Word / PDFs
        ns = ns.replace('“', '"').replace('”', '"').replace('’', "'")
        ns = ns.replace('–', '-').replace('—', '-')
        ns = ns.replace('…', '...')
        return ns.strip()
    
    # Custom styles
    title_style = ParagraphStyle(
        'FormTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        alignment=1, # Centered
        spaceAfter=6
    )
    
    label_style = ParagraphStyle(
        'FormLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=9,
        textColor=colors.black
    )
    
    value_style = ParagraphStyle(
        'FormValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=9,
        textColor=colors.black
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=10,
        spaceBefore=10,
        spaceAfter=5
    )
    
    grid_header_style = ParagraphStyle(
        'GridHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8,
        alignment=1,
        textColor=colors.black
    )
    
    grid_value_style = ParagraphStyle(
        'GridValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=9,
        alignment=1,
        textColor=colors.black
    )

    grid_value_left_style = ParagraphStyle(
        'GridValueLeft',
        parent=grid_value_style,
        alignment=0,  # left
    )

    edu_value_style = ParagraphStyle(
        'EduValue',
        parent=grid_value_style,
        fontSize=8,
        leading=9,
        alignment=0,  # left for readability in narrow columns
    )
    
    story = []
    
    # --- PAGE 1 ---
    story.append(Paragraph("APPLICATION FORM FOR FACULTY POSITION", title_style))
    
    # 1. Advertisement and post applied info
    advt_no = _norm(candidate_data.get("advt_no") or "")
    reg_no = _norm(candidate_data.get("registration_no") or "")
    post = _norm(candidate_data.get("post_applied_for") or "")
    specialisation = _norm(candidate_data.get("specialisation") or "")
    
    advt_data = [
        [Paragraph(f"ADVT NO: {advt_no}", label_style), Paragraph("", label_style)],
        [Paragraph(f"REGISTRATION NO: {reg_no}", label_style), Paragraph("", label_style)],
        [Paragraph(f"APPLICATION FOR THE POST OF: {post}", label_style), Paragraph("", label_style)],
        [Paragraph(f"SPECIALISATION: {specialisation}", label_style), Paragraph("", label_style)]
    ]
    
    page_width, _ = A4
    usable_width = page_width - doc.leftMargin - doc.rightMargin
    half = usable_width / 2.0
    advt_table = Table(advt_data, colWidths=[half, half], rowHeights=[16, 16, 16, 16])
    advt_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (1,0), (1,1)),
        ('SPAN', (0,2), (1,2)),
        ('SPAN', (0,3), (1,3)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(advt_table)
    story.append(Spacer(1, 8))
    
    # 2. Personal Details Table
    name = _norm(candidate_data.get("name") or "")
    dob = _norm(candidate_data.get("dob") or "")
    age = _norm(candidate_data.get("age") or "")
    father = _norm(candidate_data.get("father_name") or "")
    mother = _norm(candidate_data.get("mother_name") or "")
    nationality = _norm(candidate_data.get("nationality") or "")
    pob = _norm(candidate_data.get("place_of_birth") or "")
    email = _norm(candidate_data.get("email") or "")
    phone = _norm(candidate_data.get("phone") or "")
    gender_marital = _norm(candidate_data.get("gender_marital_status") or "")
    category = candidate_data.get("category") or ""
    religion = candidate_data.get("religion") or ""
    husband = candidate_data.get("husband_name") or ""
    
    father_occ = candidate_data.get("father_occupation") or ""
    mother_occ = candidate_data.get("mother_occupation") or ""
    husband_occ = candidate_data.get("husband_occupation") or ""
    other_cat = candidate_data.get("other_category") or ""
    
    personal_data = [
        [Paragraph(f"NAME IN FULL: {name}", label_style), Paragraph(f"DOB: {dob}", label_style), Paragraph(f"AGE: {age}", label_style)],
        [Paragraph(f"FATHER'S NAME: {father}", label_style), Paragraph(f"OCCUPATION: {father_occ}", label_style), Paragraph("", label_style)],
        [Paragraph(f"MOTHER'S NAME: {mother}", label_style), Paragraph(f"OCCUPATION: {mother_occ}", label_style), Paragraph("", label_style)],
        [Paragraph(f"NATIONALITY: {nationality}", label_style), Paragraph(f"PLACE OF BIRTH: {pob}", label_style), Paragraph("", label_style)],
        [Paragraph(f"EMAIL ID: {email}", label_style), Paragraph(f"MOBILE NO.: {phone}", label_style), Paragraph("", label_style)],
        [Paragraph(f"GENDER/MARITAL STATUS: {gender_marital}", label_style), Paragraph(f"CATEGORY: {category}", label_style), Paragraph("", label_style)],
        [Paragraph(f"RELIGION: {religion}", label_style), Paragraph(f"HUSBAND NAME: {husband}", label_style), Paragraph("", label_style)],
        [Paragraph(f"OTHER CATEGORY: {other_cat}", label_style), Paragraph(f"OCCUPATION: {husband_occ}", label_style), Paragraph("", label_style)],
    ]
    
    personal_table = Table(
        personal_data,
        colWidths=[usable_width * 0.40, usable_width * 0.30, usable_width * 0.30],
        rowHeights=[16] * len(personal_data),
    )
    personal_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (1,1), (2,1)),
        ('SPAN', (1,2), (2,2)),
        ('SPAN', (1,3), (2,3)),
        ('SPAN', (1,4), (2,4)),
        ('SPAN', (1,5), (2,5)),
        ('SPAN', (1,6), (2,6)),
        ('SPAN', (1,7), (2,7)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(personal_table)
    
    # 3. Particulars of Educational Qualification Table
    story.append(Paragraph("Particulars of Educational Qualification", section_title_style))
    
    edu_headers = [
        Paragraph("Sl.<br/>No.", grid_header_style),
        Paragraph("Degree", grid_header_style),
        Paragraph("Other<br/>Degree", grid_header_style),
        Paragraph("Branch/<br/>Specialization", grid_header_style),
        Paragraph("Reseach<br/>Area", grid_header_style),
        Paragraph("Name of the<br/>Institute", grid_header_style),
        Paragraph("Name of the<br/>University", grid_header_style),
        Paragraph("Year of<br/>Passing", grid_header_style),
        Paragraph("% of<br/>Marks", grid_header_style),
        Paragraph("CGPA", grid_header_style),
        Paragraph("Class/<br/>Division", grid_header_style),
        Paragraph("No. of<br/>Atempt", grid_header_style)
    ]
    
    edu_rows = [edu_headers]
    
    # Parse education list
    raw_edu_list = candidate_data.get("education", [])

    # Heuristic: filter out entries that look like experience/profile prose or headers
    def _looks_like_education_entry(s: str) -> bool:
        if not s:
            return False
        s2 = s.strip()
        # Very long paragraphs are likely summary/experience, not education rows
        if len(s2) > 240:
            return False
        low = s2.lower()
        # Degree keywords or institution indicators strongly indicate education
        degree_kw = ["ph.d", "phd", "m.tech", "mtech", "mca", "bca", "b.tech", "btech", "b.e", "master", "bachelor", "diploma", "s.s.c", "hsc", "class xii", "class x"]
        if any(k in low for k in degree_kw):
            return True
        if "university" in low or "college" in low or "institute" in low:
            # prefer kept if it also contains a year or degree-like token
            if re.search(r"\b(19|20)\d{2}\b", low) or any(k in low for k in ["ph.d", "m.tech", "mtech", "mca", "bca"]):
                return True
            # otherwise still accept shorter institute mentions
            if len(s2) < 120:
                return True
        return False

    filtered_edu = [e for e in raw_edu_list if _looks_like_education_entry(e)]
    # If filtering removed everything, fall back to original list
    if not filtered_edu:
        filtered_edu = raw_edu_list

    parsed_edu = [parse_education_entry(e) for e in filtered_edu]
    
    # Degree priority order for display
    degree_priority = [
        "Ph.D.", "M.Tech.", "M.E.", "M.Sc.", "MBA", "MCA",
        "B.E. / B.Tech", "BCA", "B.Sc.",
        "Diploma", "HSC / Intermediate", "S.S.C."
    ]

    # Collect unique degrees found, preserving priority order
    seen_degrees = set()
    ordered_edu = []
    for target in degree_priority:
        for pe in parsed_edu:
            if pe["degree"] == target and target not in seen_degrees:
                ordered_edu.append(pe)
                seen_degrees.add(target)
                break
    # Append any remaining parsed entries not in priority list
    for pe in parsed_edu:
        if pe["degree"] not in seen_degrees and pe["degree"]:
            ordered_edu.append(pe)
            seen_degrees.add(pe["degree"])

    # If nothing extracted at all, show at least 3 blank placeholder rows
    if not ordered_edu:
        for d in ["Ph.D.", "M.Tech.", "B.E. / B.Tech"]:
            ordered_edu.append({"degree": d, "other_degree": "", "spec": "",
                                 "inst": "", "univ": "", "year": "",
                                 "percent": "", "cgpa": "", "division": ""})

    # Scale column widths to fit A4 usable width while keeping the same proportions.
    edu_col_widths_base = [20, 42, 40, 58, 48, 58, 58, 38, 30, 30, 48, 34]
    edu_scale = usable_width / float(sum(edu_col_widths_base))
    edu_col_widths = [w * edu_scale for w in edu_col_widths_base]

    for idx, pe in enumerate(ordered_edu, 1):
        edu_row_h = 18
        row = [
            Paragraph(str(idx), grid_value_style),
            Paragraph(pe["degree"], grid_value_style),
            Paragraph(pe["other_degree"], grid_value_style),
            fit_cell(pe["spec"], edu_value_style, edu_col_widths[3], edu_row_h),
            Paragraph("", grid_value_style),
            fit_cell(pe["inst"], edu_value_style, edu_col_widths[5], edu_row_h),
            fit_cell(pe["univ"], edu_value_style, edu_col_widths[6], edu_row_h),
            Paragraph(pe["year"], grid_value_style),
            Paragraph(pe["percent"], grid_value_style),
            Paragraph(pe["cgpa"], grid_value_style),
            Paragraph(pe["division"], grid_value_style),
            Paragraph("", grid_value_style)
        ]
        edu_rows.append(row)
        
    # Slightly taller rows so education text stays readable.
    edu_row_heights = [18] + ([18] * (len(edu_rows) - 1))
    edu_table = Table(edu_rows, colWidths=edu_col_widths, rowHeights=edu_row_heights)
    edu_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(edu_table)
    
    # 4. Titles PG/Ph.D. Table
    story.append(Paragraph("Titles PG/Ph.D.", section_title_style))
    thesis_headers = [
        Paragraph("Sl.No.", grid_header_style),
        Paragraph("Degree", grid_header_style),
        Paragraph("Title of Thesis", grid_header_style),
        Paragraph("Guide", grid_header_style),
        Paragraph("University", grid_header_style)
    ]
    
    thesis_rows = [thesis_headers]
    thesis_list = candidate_data.get("thesis_info", [])
    
    # Ensure at least 2 rows
    for idx in range(1, 3):
        if idx - 1 < len(thesis_list):
            t = thesis_list[idx - 1]
            row = [
                Paragraph(str(idx), grid_value_style),
                Paragraph(t.get("degree", ""), grid_value_style),
                Paragraph(t.get("title", ""), grid_value_style),
                Paragraph(t.get("guide", ""), grid_value_style),
                Paragraph(t.get("university", ""), grid_value_style)
            ]
        else:
            row = [
                Paragraph(str(idx), grid_value_style),
                Paragraph("Ph.D." if idx==1 else "PG", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style)
            ]
        thesis_rows.append(row)
        
    thesis_col_base = [30, 60, 214, 100, 100]
    thesis_scale = usable_width / float(sum(thesis_col_base))
    thesis_col = [w * thesis_scale for w in thesis_col_base]
    thesis_table = Table(thesis_rows, colWidths=thesis_col, rowHeights=[16] + ([14] * (len(thesis_rows) - 1)))
    thesis_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(thesis_table)
    
    # 5. Details of Experience Table (Teaching)
    story.append(Paragraph("Details of Experience", section_title_style))
    
    # Intelligent experience classification
    raw_exp_list = candidate_data.get("experience", [])
    parsed_exp_list = [parse_experience_entry(e) for e in raw_exp_list]
    
    teaching_exp = []
    research_exp = []
    industrial_exp = []
    
    # 1. Try to extract Ph.D. graduation year
    parsed_edu = [parse_education_entry(e) for e in candidate_data.get("education", [])]
    phd_year = None
    for pe in parsed_edu:
        if pe["degree"] == "Ph.D." and pe["year"]:
            try:
                phd_year = int(pe["year"])
            except ValueError:
                pass
                
    has_phd = phd_year is not None or any("ph.d" in edu.lower() or "phd" in edu.lower() for edu in candidate_data.get("education", []))
    
    for exp in parsed_exp_list:
        org_lower = exp["org"].lower()
        desig_lower = exp["desig"].lower()
        
        # Calculate pre/post Ph.D. years
        exp["post_phd"] = "No"
        pre_years = 0
        post_years = 0
        
        start_year = None
        if exp["doj"]:
            m_year = re.search(r'\b((?:19|20)\d{2})\b', exp["doj"])
            if m_year:
                start_year = int(m_year.group(1))
                
        end_year = None
        if exp["dol"]:
            if exp["dol"].lower() == "present":
                end_year = 2026
            else:
                m_year = re.search(r'\b((?:19|20)\d{2})\b', exp["dol"])
                if m_year:
                    end_year = int(m_year.group(1))
                    
        total_years = 0
        try:
            total_years = int(exp.get("years", 0))
        except:
            pass
            
        if phd_year and start_year:
            if start_year >= phd_year:
                exp["post_phd"] = "Yes"
                post_years = total_years
            elif end_year and end_year <= phd_year:
                exp["post_phd"] = "No"
                pre_years = total_years
            else:
                pre_years = min(total_years, phd_year - start_year)
                post_years = max(0, total_years - pre_years)
                if post_years > 0:
                    exp["post_phd"] = "Yes"
        else:
            if has_phd:
                exp["post_phd"] = "Yes"
                post_years = total_years
            else:
                exp["post_phd"] = "No"
                pre_years = total_years
                
        exp["pre_years_calculated"] = pre_years
        exp["post_years_calculated"] = post_years
        
        # Experience type classification
        is_research = False
        for w in ["researcher", "scientist", "fellow", "postdoc", "research associate", "ra"]:
            if re.search(r'\b' + re.escape(w) + r'\b', desig_lower):
                is_research = True
                break
        if re.search(r'\bresearch\b', org_lower):
            is_research = True
            
        if is_research:
            research_exp.append(exp)
        elif any(w in org_lower for w in ["ltd", "limited", "pvt", "inc", "co.", "corporation", "corp", "group", "associate", "associates", "club", "solutions", "technologies", "firm", "labs", "systems", "hospital", "bank", "software", "google", "meta", "amazon", "microsoft", "apple", "xorblin"]):
            industrial_exp.append(exp)
        else:
            if any(w in desig_lower for w in ["assistant", "professor", "lecturer", "teacher", "instructor", "tutor", "teaching assistant", "ta"]) or any(w in org_lower for w in ["university", "college", "institute", "school", "jklu", "academy"]):
                teaching_exp.append(exp)
            else:
                teaching_exp.append(exp)
                
    # Calculate teaching durations
    total_pre_teaching = sum(exp.get("pre_years_calculated", 0) for exp in teaching_exp)
    total_post_teaching = sum(exp.get("post_years_calculated", 0) for exp in teaching_exp)
            
    teaching_exp_str = f"Teaching of Experience      Total Pre Ph.D. Experience : {total_pre_teaching} Yr(s) 0 Months(s)      Total Post Ph.D. Experience : {total_post_teaching} Yr(s). 0 Month (s)"
    story.append(Paragraph(teaching_exp_str, label_style))
    story.append(Spacer(1, 3))
    
    exp_headers = [
        Paragraph("Sl.No", grid_header_style),
        Paragraph("Name of the organizatio where employed", grid_header_style),
        Paragraph("Designation", grid_header_style),
        Paragraph("Post Ph.D.", grid_header_style),
        Paragraph("Date of Joining", grid_header_style),
        Paragraph("Date of Leaving", grid_header_style),
        Paragraph("Post Ph.D. Exp.", grid_header_style),
        Paragraph("Last Pay Band and Grade Pay", grid_header_style)
    ]
    
    teaching_rows = [exp_headers]
    for idx in range(1, 3):
        if idx - 1 < len(teaching_exp):
            t = teaching_exp[idx - 1]
            post_exp_str = f"{t['post_years_calculated']} Yr(s)" if t['post_years_calculated'] > 0 else ""
            row = [
                Paragraph(str(idx), grid_value_style),
                Paragraph(t["org"], grid_value_style),
                Paragraph(t["desig"], grid_value_style),
                Paragraph(t["post_phd"], grid_value_style),
                Paragraph(t["doj"], grid_value_style),
                Paragraph(t["dol"], grid_value_style),
                Paragraph(post_exp_str, grid_value_style),
                Paragraph(t["pay"] if t["pay"] != "N/A" else "", grid_value_style)
            ]
        else:
            row = [
                Paragraph(str(idx), grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style)
            ]
        teaching_rows.append(row)
        
    exp_col_base = [24, 150, 80, 40, 60, 60, 40, 50]
    exp_scale = usable_width / float(sum(exp_col_base))
    exp_col = [w * exp_scale for w in exp_col_base]
    teaching_table = Table(teaching_rows, colWidths=exp_col, rowHeights=[16] + ([14] * (len(teaching_rows) - 1)))
    teaching_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(teaching_table)
    
    # PageBreak to maintain standard 3 page format
    story.append(PageBreak())
    
    # --- PAGE 2 ---
    # 6. Research Experience Table
    total_pre_research = sum(exp.get("pre_years_calculated", 0) for exp in research_exp)
    total_post_research = sum(exp.get("post_years_calculated", 0) for exp in research_exp)
            
    story.append(Paragraph("Research Experience", section_title_style))
    story.append(Paragraph(f"Total Research Experience : {total_pre_research + total_post_research} Yr(s). 0 Month(s)", label_style))
    story.append(Spacer(1, 3))
    
    research_rows = [
        [
            Paragraph("Sl.No", grid_header_style),
            Paragraph("Name of the organizatio where employed", grid_header_style),
            Paragraph("Designation", grid_header_style),
            Paragraph("Post Ph.D.", grid_header_style),
            Paragraph("Date of Joining", grid_header_style),
            Paragraph("Date of Leaving", grid_header_style),
            Paragraph("Post Ph.D. Exp.", grid_header_style),
            Paragraph("Last Pay Band and Grade Pay", grid_header_style)
        ]
    ]
    
    for idx in range(1, 3):
        if idx - 1 < len(research_exp):
            r = research_exp[idx - 1]
            post_exp_str = f"{r['post_years_calculated']} Yr(s)" if r['post_years_calculated'] > 0 else ""
            research_rows.append([
                Paragraph(str(idx), grid_value_style),
                Paragraph(r["org"], grid_value_style),
                Paragraph(r["desig"], grid_value_style),
                Paragraph(r["post_phd"], grid_value_style),
                Paragraph(r["doj"], grid_value_style),
                Paragraph(r["dol"], grid_value_style),
                Paragraph(post_exp_str, grid_value_style),
                Paragraph(r["pay"] if r["pay"] != "N/A" else "", grid_value_style)
            ])
        else:
            research_rows.append([
                Paragraph(str(idx), grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style)
            ])
        
    research_table = Table(research_rows, colWidths=exp_col, rowHeights=[16] + ([14] * (len(research_rows) - 1)))
    research_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(research_table)
    
    # 7. Industrial Experience Table
    total_pre_industrial = sum(exp.get("pre_years_calculated", 0) for exp in industrial_exp)
    total_post_industrial = sum(exp.get("post_years_calculated", 0) for exp in industrial_exp)
            
    story.append(Paragraph("Industrial Experience", section_title_style))
    story.append(Paragraph(f"Total Experience : {total_pre_industrial + total_post_industrial} Yr(s). 0 Month(s)", label_style))
    story.append(Spacer(1, 3))
    
    ind_rows = [
        [
            Paragraph("Sl.No", grid_header_style),
            Paragraph("Name of the organizatio where employed", grid_header_style),
            Paragraph("Designation", grid_header_style),
            Paragraph("Post Ph.D.", grid_header_style),
            Paragraph("Date of Joining", grid_header_style),
            Paragraph("Date of Leaving", grid_header_style),
            Paragraph("Post Ph.D. Exp.", grid_header_style),
            Paragraph("Last Pay Band and Grade Pay", grid_header_style)
        ]
    ]
    
    for idx in range(1, 3):
        if idx - 1 < len(industrial_exp):
            i = industrial_exp[idx - 1]
            post_exp_str = f"{i['post_years_calculated']} Yr(s)" if i['post_years_calculated'] > 0 else ""
            ind_rows.append([
                Paragraph(str(idx), grid_value_style),
                Paragraph(i["org"], grid_value_style),
                Paragraph(i["desig"], grid_value_style),
                Paragraph(i["post_phd"], grid_value_style),
                Paragraph(i["doj"], grid_value_style),
                Paragraph(i["dol"], grid_value_style),
                Paragraph(post_exp_str, grid_value_style),
                Paragraph(i["pay"] if i["pay"] != "N/A" else "", grid_value_style)
            ])
        else:
            ind_rows.append([
                Paragraph(str(idx), grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style)
            ])
        
    ind_table = Table(ind_rows, colWidths=exp_col, rowHeights=[16] + ([14] * (len(ind_rows) - 1)))
    ind_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(ind_table)
    
    # 8. Total Research Publication/Presentation Table
    story.append(Paragraph("Total Research Publication/Presentation", section_title_style))
    pub_headers = [
        Paragraph("Sl. No.", grid_header_style),
        Paragraph("Conf./Jou. N./IN. Pub./ Acc. Valu. No.", grid_header_style),
        Paragraph("Pub. Type/ Year ISBN No.", grid_header_style),
        Paragraph("SCI/ Non-SCI", grid_header_style),
        Paragraph("Title of Paper", grid_header_style),
        Paragraph("Author1", grid_header_style),
        Paragraph("Author2", grid_header_style),
        Paragraph("Author3", grid_header_style),
        Paragraph("Author4", grid_header_style),
        Paragraph("Name of journal", grid_header_style)
    ]
    
    pub_col_base = [20, 60, 50, 40, 134, 40, 40, 40, 40, 40]
    pub_scale = usable_width / float(sum(pub_col_base))
    pub_col = [w * pub_scale for w in pub_col_base]

    pub_rows = [pub_headers]
    pubs = candidate_data.get("publications", [])
    
    for idx in range(1, 11):
        if idx - 1 < len(pubs):
            p = pubs[idx - 1]
            details = parse_publication_details(p)
            # More height so text can wrap without getting tiny.
            row_h = 28
            row = [
                Paragraph(str(idx), grid_value_style),
                Paragraph(details["type"], grid_value_style),
                Paragraph(f"{details['type']} / {details['year']}" if details['year'] else "", grid_value_style),
                Paragraph("SCI" if "sci" in p.lower() else "Non-SCI", grid_value_style),
                fit_cell(details["title"], grid_value_left_style, pub_col[4], row_h),
                Paragraph(name.split()[0] if name else "", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                fit_cell(details["journal"], grid_value_left_style, pub_col[9], row_h),
            ]
        else:
            row = [
                Paragraph(str(idx), grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style)
            ]
        pub_rows.append(row)
        
    pub_table = Table(pub_rows, colWidths=pub_col, rowHeights=[18] + ([28] * (len(pub_rows) - 1)))
    pub_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(pub_table)
    
    # 9. Total Books Published
    story.append(Paragraph("Total Books Published", section_title_style))
    book_headers = [
        Paragraph("Sl.No.", grid_header_style),
        Paragraph("Title of The Book", grid_header_style),
        Paragraph("Publisher Name", grid_header_style),
        Paragraph("Author Name", grid_header_style)
    ]
    book_rows = [book_headers]
    for idx in range(1, 3):
        book_rows.append([
            Paragraph(str(idx), grid_value_style),
            Paragraph("", grid_value_style),
            Paragraph("", grid_value_style),
            Paragraph("", grid_value_style)
        ])
    book_col_base = [30, 254, 110, 110]
    book_scale = usable_width / float(sum(book_col_base))
    book_col = [w * book_scale for w in book_col_base]
    book_table = Table(book_rows, colWidths=book_col, rowHeights=[16] + ([14] * (len(book_rows) - 1)))
    book_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(book_table)
    
    # 10. Thesis / Dissertation Guided
    story.append(Spacer(1, 5))
    guided_data = [
        [Paragraph("No. Of PG Dissertations/ Ph.D. thesis guided: P.G. - 0", label_style), Paragraph("Ph.D - 0", label_style)],
        [Paragraph("Title of Ph.D. Thesis:", label_style), Paragraph("", label_style)]
    ]
    guided_table = Table(guided_data, colWidths=[half, half], rowHeights=[16, 16])
    guided_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (0,1), (1,1)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(guided_table)
    
    # 11. Patents Table
    story.append(Paragraph("Patents", section_title_style))
    patent_headers = [
        Paragraph("S.l No.", grid_header_style),
        Paragraph("Name of Patent", grid_header_style),
        Paragraph("Year", grid_header_style),
        Paragraph("Organisation", grid_header_style)
    ]
    patent_rows = [patent_headers]
    for idx in range(1, 3):
        patent_rows.append([
            Paragraph(str(idx), grid_value_style),
            Paragraph("", grid_value_style),
            Paragraph("", grid_value_style),
            Paragraph("", grid_value_style)
        ])
    patent_table = Table(patent_rows, colWidths=book_col, rowHeights=[16] + ([14] * (len(patent_rows) - 1)))
    patent_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(patent_table)
    
    # 12. Consultant Table
    story.append(Paragraph("Consultant", section_title_style))
    consultant_headers = [
        Paragraph("S.l No.", grid_header_style),
        Paragraph("Name of Patent", grid_header_style),
        Paragraph("Year", grid_header_style),
        Paragraph("Organisation", grid_header_style)
    ]
    consultant_rows = [consultant_headers]
    for idx in range(1, 3):
        consultant_rows.append([
            Paragraph(str(idx), grid_value_style),
            Paragraph("", grid_value_style),
            Paragraph("", grid_value_style),
            Paragraph("", grid_value_style)
        ])
    consultant_table = Table(consultant_rows, colWidths=book_col, rowHeights=[16] + ([14] * (len(consultant_rows) - 1)))
    consultant_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(consultant_table)
    
    # PageBreak to maintain standard 3 page format
    story.append(PageBreak())
    
    # --- PAGE 3 ---
    # Text blocks for pay expectation and memberships
    story.append(Paragraph("Additional Professional Declarations", section_title_style))
    
    pay_expected = candidate_data.get("pay_expected") or ""
    joining_time = candidate_data.get("joining_time") or ""
    
    # (i) Professional body memberships — from dedicated memberships field
    memberships_list = candidate_data.get("memberships", []) or []
    # Fallback: also check involvement for membership-like items
    if not memberships_list:
        memberships_list = [x for x in (candidate_data.get("involvement", []) or [])
                            if any(kw in x.lower() for kw in ["member", "fellow", "society", "association", "ieee", "acm", "iste"])]
    memberships_str = "; ".join(memberships_list) if memberships_list else "-"
    
    # (ii) Achievements in sports/extracurricular
    achievements_list = (candidate_data.get("achievements", []) or []) + (candidate_data.get("awards", []) or [])
    achievements_str = "; ".join(achievements_list) if achievements_list else "-"
    
    # (iii) Administrative / committee responsibilities
    admin_list = candidate_data.get("administrative_works", []) or []
    admin_str = "; ".join(admin_list) if admin_list else "-"
    
    # (iv) Workshops / FDPs attended
    workshops_list = candidate_data.get("workshops", []) or []
    workshops_str = "; ".join(workshops_list) if workshops_list else "-"
    
    # Give enough height so long lines wrap at readable size.
    extra_row_h = 40
    extra_data = [
        [fit_cell(f"(a) Minimum Pay expected: Basic and AGP: - {pay_expected}", label_style, usable_width, extra_row_h)],
        [fit_cell(f"(b) Time required to join the institure, If Selected: - {joining_time}", label_style, usable_width, extra_row_h)],
        [fit_cell(f"(i) Memberships/Fellowship and position of responsibility in Professional Societies : - {memberships_str}", label_style, usable_width, extra_row_h)],
        [fit_cell(f"(ii) Achievements in sports and extra-curricular activities (including N.C.C.) :- {achievements_str}", label_style, usable_width, extra_row_h)],
    ]
    extra_table = Table(extra_data, colWidths=[usable_width], rowHeights=[extra_row_h] * len(extra_data))
    extra_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(extra_table)
    story.append(Spacer(1, 10))
    
    # 13. Professional Referees Table
    story.append(Paragraph("Name and addresses of two professional referees (who are not related to the applicant) who are in a position to testify from their personal knowledge as to the fitness of the application for the post applied for:", label_style))
    story.append(Spacer(1, 3))
    
    ref_headers = [
        Paragraph("Sl.No.", grid_header_style),
        Paragraph("Name", grid_header_style),
        Paragraph("Designation", grid_header_style),
        Paragraph("Address", grid_header_style),
        Paragraph("Email ID", grid_header_style)
    ]
    ref_rows = [ref_headers]
    parsed_referees = candidate_data.get("referees", [])
    
    for idx in range(1, 3):
        if idx - 1 < len(parsed_referees):
            ref = parsed_referees[idx - 1]
            ref_rows.append([
                Paragraph(str(idx), grid_value_style),
                Paragraph(ref.get("name", ""), grid_value_style),
                Paragraph(ref.get("designation", ""), grid_value_style),
                Paragraph(ref.get("address", ""), grid_value_style),
                Paragraph(ref.get("email", ""), grid_value_style)
            ])
        else:
            ref_rows.append([
                Paragraph(str(idx), grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style),
                Paragraph("", grid_value_style)
            ])
            
    ref_col_base = [30, 100, 100, 174, 100]
    ref_scale = usable_width / float(sum(ref_col_base))
    ref_col = [w * ref_scale for w in ref_col_base]
    ref_table = Table(ref_rows, colWidths=ref_col, rowHeights=[16] + ([14] * (len(ref_rows) - 1)))
    ref_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(ref_table)
    
    # 14. Institute Reference
    story.append(Paragraph("Institure Reference", section_title_style))
    inst_ref_name = candidate_data.get("institute_reference_name") or ""
    inst_ref_contact = candidate_data.get("institute_reference_contact") or ""
    
    inst_ref_data = [
        [Paragraph(f"Name: {inst_ref_name}", label_style), Paragraph(f"Contact Number: {inst_ref_contact}", label_style)]
    ]
    inst_ref_table = Table(inst_ref_data, colWidths=[half, half], rowHeights=[16])
    inst_ref_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(inst_ref_table)
    story.append(Spacer(1, 20))
    
    # 15. Declaration and signature block
    # Use a consistent upright font for the declaration to avoid fallback/italic inconsistencies
    decl_style = ParagraphStyle(
        'Declaration',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        spaceAfter=30
    )
    story.append(Paragraph(_norm("I do hereby solemnly declare that the information given above is correct to the best of my knowledge and belief. With date of final submit and signature with name."), decl_style))
    
    sig_data = [
        [Paragraph(f"Date : {candidate_data.get('submission_date', '')}", label_style), Paragraph("Signature of Candidate: ___________________________", label_style)]
    ]
    sig_col_base = [150, 354]
    sig_scale = usable_width / float(sum(sig_col_base))
    sig_col = [w * sig_scale for w in sig_col_base]
    sig_table = Table(sig_data, colWidths=sig_col, rowHeights=[16])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sig_table)
    
    # Build document with a consistent form-like outer border on every page.
    # (We intentionally avoid extra headers/footers to match the reference form.)
    doc.build(
        story,
        onFirstPage=draw_form_frame,
        onLaterPages=draw_form_frame,
    )
    return output_path
