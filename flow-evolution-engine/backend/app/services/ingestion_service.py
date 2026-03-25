from io import BytesIO
from pypdf import PdfReader


def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages).strip()
