from dotenv import load_dotenv
import os
from git import Repo

class GitHubRepo:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN", None)
    
    def clone_repo(self, destination_path: str):
        if self.github_token:
            authed_url = self.repo_url.replace("https://", f"https://{self.github_token}@")
        else:
            authed_url = self.repo_url
        Repo.clone_from(authed_url, destination_path)
