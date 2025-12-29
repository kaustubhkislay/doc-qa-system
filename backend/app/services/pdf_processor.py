from pypdf import PdfReader
from io import BytesIO
from dataclasses import dataclass


@dataclass
class PageContent:
    """Content extracted from a single PDF page."""
    page_number: int
    text: str


@dataclass
class PDFContent:
    """Full content extracted from a PDF."""
    pages: list[PageContent]
    page_count: int
    full_text: str


def extract_pdf_content(pdf_bytes: bytes) -> PDFContent:
    """Extract text content from a PDF file."""
    pdf_file = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    
    pages = []
    full_text_parts = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append(PageContent(page_number=i + 1, text=text))
        full_text_parts.append(f"[Page {i + 1}]\n{text}")
    
    return PDFContent(
        pages=pages,
        page_count=len(reader.pages),
        full_text="\n\n".join(full_text_parts)
    )