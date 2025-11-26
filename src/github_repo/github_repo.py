import os

from dotenv import load_dotenv
from git import Repo


class GitHubRepo:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN", None)

    def clone_repo(self, destination_path: str) -> str:
        if self.github_token:
            authed_url = self.repo_url.replace("https://", f"https://{self.github_token}@")
        else:
            authed_url = self.repo_url
        path = os.path.join(destination_path, self.get_repo_name())
        if os.path.exists(path):
            return path
        Repo.clone_from(authed_url, path)
        return path

    def get_repo_name(self) -> str:
        return self.repo_url.replace("https://github.com/", "").rstrip("/").split("/")[-1]
