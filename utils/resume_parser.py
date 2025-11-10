import os
from typing import Optional
def extract_text_from_file(path: str) -> str:
    """
    Try to extract text from PDF using PyPDF2. If fails, returns empty string.
    """
    text = ""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        try:
            import PyPDF2
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            # fallback: return filename as minimal content
            text = ""
    else:
        # Try reading as text file
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except:
            text = ""
    return text or ""
