import tempfile
import urllib.request
import shutil
import re

from pdfminer.high_level import extract_text as extract_pdf_text

class GitHubLinkExtractor:
    def __init__(self, pdf_url: str):
        self.pdf_url = pdf_url

    def run(self):
        pdf_path = self.download_pdf()
        text = self.extract_text(pdf_path)
        print("Extracted Text:")
        print(text[:100])
        return self.extract_github_links(text)
    
    def download_pdf(self) -> str:
        """Downloads the PDF from the given URL and returns the local file path."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpf:
            print(f"Downloading PDF from {self.pdf_url} to {tmpf.name}")
            with urllib.request.urlopen(self.pdf_url) as response, open(tmpf.name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            self.pdf_path = tmpf.name
            return self.pdf_path
        
    def extract_text(self, pdf_path: str) -> str:
        """Extracts text from the given PDF file path."""
        text = extract_pdf_text(pdf_path)
        return text
    
    def extract_github_links(self, text: str) -> set['str']:
        """Extracts GitHub links from the given text."""
        urls = set()
        pattern = r'\b(?:https?://|www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s)>\]]*)?'
        matches = re.findall(pattern, text)
        for match in matches:
            urls.add(match.strip().rstrip(".,);:!?\"'"))
        return {url for url in urls if "github.com" in url}