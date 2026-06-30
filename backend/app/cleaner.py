import re
import unicodedata

def clean_text(text):
    """
    Cleans raw text extracted from PDFs or DOCX files:
    - Normalizes unicode characters
    - Standardizes bullet points and dashes
    - Cleans extra whitespaces and redundant newlines
    - Strips non-printable control characters
    """
    if not text:
        return ""
    
    # Normalize unicode (NFKC normalization to compose characters and resolve symbols)
    text = unicodedata.normalize('NFKC', text)
    
    # Replace common bullet points and special characters with standard representations
    text = re.sub(r'[\u2022\u2023\u2043\u204c\u25cf\u25cb\u25aa\u25ab\u25b6\u27a1]', '-', text)
    
    # Replace smart quotes and special hyphens
    text = re.sub(r'[\u201c\u201d\u2018\u2019]', '"', text)
    text = re.sub(r'[\u2013\u2014]', '-', text)
    
    # Strip non-printable control characters (except tab and newlines)
    text = "".join(ch for ch in text if ch == '\n' or ch == '\r' or ch == '\t' or unicodedata.category(ch)[0] != 'C')
    
    # Replace carriage returns with newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Normalize multi-newlines (maximum 2 consecutive newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip spaces at the beginning and end of each line
    lines = [line.strip() for line in text.split('\n')]
    
    # Filter out lines that are purely empty or contain only multiple hyphens/dashes (dividers)
    cleaned_lines = []
    for line in lines:
        if line:
            # Replace multiple consecutive spaces with a single space
            line = re.sub(r'[ \t]+', ' ', line)
            cleaned_lines.append(line)
        else:
            # Maintain a single empty line between paragraphs, if previous line was not empty
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
                
    # Remove trailing empty lines
    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()
        
    return "\n".join(cleaned_lines)
