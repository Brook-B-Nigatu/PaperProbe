import tempfile
import urllib.request
import shutil
import re

from pdfminer.high_level import extract_text as extract_pdf_text

class PDFParser:
    def __init__(self, pdf_path: str, is_url: bool = True):
        self.pdf_path = pdf_path
        self.text = self._extract_text(self._download_pdf()) if is_url else self._extract_text(pdf_path)
    
    def _download_pdf(self) -> str:
        """Downloads the PDF from the given URL and returns the local file path."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpf:
            print(f"Downloading PDF from {self.pdf_path} to {tmpf.name}")
            with urllib.request.urlopen(self.pdf_path) as response, open(tmpf.name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            self.pdf_path = tmpf.name
            return self.pdf_path
        
    def _extract_text(self, pdf_path: str) -> str:
        """Extracts text from the given PDF file path."""
        text = extract_pdf_text(pdf_path)
        return text
    
    def extract_github_links(self) -> set['str']:
        """Extracts GitHub links from the given text."""
        urls = set()
        pattern = r'\b(?:https?://|www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s)>\]]*)?'
        matches = re.findall(pattern, self.text)
        for match in matches:
            urls.add(match.strip().rstrip(".,);:!?\"'"))
        return {url for url in urls if "github.com" in url}
    
    def get_text(self) -> str:
        """Returns the extracted text from the PDF."""
        return self.text