from urllib.parse import urlparse
from src.preprocessing_utilities.pdf_parser import PDFParser

from .llm_service import call_llm

def get_github_links(pdf_path: str) -> list[str]:
    """Extract GitHub links from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file."""

    is_url = bool(urlparse(pdf_path).scheme in ('http', 'https'))
    pdf_parser = PDFParser(pdf_path, is_url=is_url)
    github_links = list(pdf_parser.extract_github_links())

    RANKING_PROMPT = f"""Read the following text extracted from a research paper:
    
    {pdf_parser.get_text()}

    Here are some github links extracted from the paper. Identify which of theses links
    is the main code repository for the paper or is most relevant to the paper. Only return the link, nothing else.
    Links:
    {'\n'.join(github_links)}
    """
    response = call_llm(RANKING_PROMPT)
    print(response)
    
    for i in range(len(github_links)):
        if github_links[i] in response:
            github_links[0], github_links[i] = github_links[i], github_links[0]
            break
    
    return github_links
    