"""
Resume Parser Utility - Extract text and check for keywords.
"""
import re
from pathlib import Path
from typing import List, Tuple


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from a resume file.
    Supports: .txt, .pdf (requires PyMuPDF), .docx (requires python-docx)
    """
    path = Path(file_path)
    
    if not path.exists():
        return ""
    
    suffix = path.suffix.lower()
    
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    
    elif suffix == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            # Fallback: try pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                    return text
            except ImportError:
                return "[PDF parsing unavailable: install PyMuPDF or pdfplumber]"
    
    elif suffix == ".docx":
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except ImportError:
            return "[DOCX parsing unavailable: install python-docx]"
    
    else:
        # Try reading as plain text
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except:
            return ""


def check_keywords(text: str, keywords: List[str]) -> Tuple[int, List[str]]:
    """
    Check how many keywords are found in the text.
    Returns: (match_count, list of matched keywords)
    """
    text_lower = text.lower()
    matched = []
    
    for keyword in keywords:
        # Use word boundary matching
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            matched.append(keyword)
    
    return len(matched), matched


def calculate_eligibility_score(text: str, required_keywords: List[str], bonus_keywords: List[str] = None) -> dict:
    """
    Calculate eligibility score based on keyword matching.
    
    Args:
        text: Resume text content
        required_keywords: Must-have keywords (e.g., "python", "machine learning")
        bonus_keywords: Nice-to-have keywords (e.g., "tensorflow", "pytorch")
    
    Returns:
        {
            "score": 0-100,
            "required_matched": [...],
            "bonus_matched": [...],
            "eligible": True/False (>= 50% required keywords)
        }
    """
    bonus_keywords = bonus_keywords or []
    
    req_count, req_matched = check_keywords(text, required_keywords)
    bonus_count, bonus_matched = check_keywords(text, bonus_keywords)
    
    # Calculate score: 70% weight for required, 30% for bonus
    req_score = (req_count / len(required_keywords) * 70) if required_keywords else 0
    bonus_score = (bonus_count / len(bonus_keywords) * 30) if bonus_keywords else 0
    
    total_score = min(100, req_score + bonus_score)
    
    # Eligible if at least 50% of required keywords matched
    req_threshold = len(required_keywords) * 0.5 if required_keywords else 0
    eligible = req_count >= req_threshold
    
    return {
        "score": round(total_score, 1),
        "required_matched": req_matched,
        "bonus_matched": bonus_matched,
        "eligible": eligible
    }


# Predefined keyword sets per domain
DOMAIN_KEYWORDS = {
    "AI-ML": {
        "required": ["python", "machine learning", "data", "model"],
        "bonus": ["tensorflow", "pytorch", "deep learning", "neural network", "sklearn", "numpy", "pandas", "nlp", "computer vision"]
    },
    "Fullstack": {
        "required": ["javascript", "html", "css", "api"],
        "bonus": ["react", "node", "sql", "mongodb", "typescript", "rest", "docker", "git", "python", "aws"]
    },
    "Cybersecurity": {
        "required": ["security", "network", "linux"],
        "bonus": ["penetration testing", "firewall", "encryption", "vulnerability", "siem", "incident response", "compliance", "python", "scripting"]
    }
}


def screen_resume(file_path: str, domain: str) -> dict:
    """
    Screen a resume for a specific domain.
    
    Args:
        file_path: Path to resume file
        domain: One of "AI-ML", "Fullstack", "Cybersecurity"
    
    Returns:
        Eligibility result with score and matched keywords
    """
    text = extract_text_from_file(file_path)
    
    if not text or text.startswith("["):
        return {
            "score": 0,
            "required_matched": [],
            "bonus_matched": [],
            "eligible": False,
            "error": text or "Could not extract text from resume"
        }
    
    keywords = DOMAIN_KEYWORDS.get(domain, DOMAIN_KEYWORDS["Fullstack"])
    
    return calculate_eligibility_score(
        text,
        keywords["required"],
        keywords["bonus"]
    )
