from urllib.parse import urlparse

from langchain_core.messages import (HumanMessage, SystemMessage)

from .llm_service import call_llm, execute_agentic_task
from src.github_repo.github_repo import GitHubRepo
from src.preprocessing_utilities.pdf_parser import PDFParser
from src.tool_providers.file_system_tools_provider import FileSystemToolsProvider
from src.tool_providers.code_analysis_tools_provider import CodeAnalysisToolsProvider
from src.tool_providers.venv_tools_provider import VenvToolsProvider
from src.tool_providers.github_stats_tools_provider import GitHubStatsToolsProvider

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

def get_example_script(base_dir: str) -> str:
    """Uses an LLM-based agent to generate an example script demonstrating the main functionality of the codebase
    located at the given base directory.

    Args:
        base_dir (str): The base directory of the code repository.

    Returns:
        str: The generated example script.
    """
    fs_tools_provider = FileSystemToolsProvider(base_dir)
    code_analysis_tools_provider = CodeAnalysisToolsProvider(base_dir)
    venv_tools_provider = VenvToolsProvider(base_dir)

    script_gen_tools = fs_tools_provider.get_tool_list() + \
        code_analysis_tools_provider.get_tool_list() + \
        venv_tools_provider.get_tool_list()
    
    script_gen_messages = [
        SystemMessage("You are an experienced Python developer. Use the tools at your disposal carefully. Always stick to the correct formatting when using tool calls."),
        HumanMessage("Understand the project and generate a working script that demonstrates its main functionality. Use the tools to run, validate and refine your script as much as possible. On your final response, output just the final version of the script and nothing else.")
    ]

    script = execute_agentic_task(
        tools=script_gen_tools,
        messages=script_gen_messages
    )

    return script

def basic_analysis(github_url: str) -> str:
    """Performs a basic analysis of the GitHub repository at the given URL. It includes some
    information about the repository and example scripts of usage.

    Args:
        github_url (str): The URL of the GitHub repository.

    Returns:
        str: A summary of the repository in markdown format.
    """
    if not github_url.startswith("https://"):
        github_url = "https://" + github_url

    repo = GitHubRepo(github_url)
    base_dir = repo.clone_repo("cloned_repos")

    example_script = get_example_script(base_dir)

    

