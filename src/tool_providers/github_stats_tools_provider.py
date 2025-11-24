from github import Github
from datetime import datetime
from dotenv import load_dotenv
import os
from .tool_provider_base import ToolProviderBase


class GitHubStatsToolsProvider(ToolProviderBase):
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN", None)
        self._github_client = None
        self._repo_info = None
    
    def _get_github_client(self):
        if self._github_client is None:
            if self.github_token:
                self._github_client = Github(self.github_token)
            else:
                self._github_client = Github()
        return self._github_client
    
    def _get_repo_info(self):
        if self._repo_info is None:
            g = self._get_github_client()
            # Extract owner/repo from URL
            repo_path = self.repo_url.replace("https://github.com/", "").rstrip("/")
            self._repo_info = g.get_repo(repo_path)
        return self._repo_info
    
    def get_basic_info(self) -> str:
        """Get comprehensive repository information including name, description, creation date, age, 
        languages, popularity metrics, activity info, last commit date, contributors, documentation, 
        license, and health status. This is the primary tool for getting repository overview."""
        
        try:
            repo = self._get_repo_info()
            
            created_at = repo.created_at
            age_days = (datetime.now() - created_at).days
            age_years = round(age_days / 365.25, 2)

            primary_language = repo.language or "Not specified"

            last_commit_date = repo.pushed_at.strftime('%Y-%m-%d')
            days_since_commit = (datetime.now() - repo.pushed_at).days
            try:
                commit_count = repo.get_commits().totalCount
            except:
                commit_count = "Unknown"
            
            try:
                total_contributors = repo.get_contributors().totalCount
            except:
                total_contributors = "Unknown"
            
            docs_url = "Not specified"
            if repo.has_wiki:
                docs_url = f"{repo.html_url}/wiki"
            elif repo.homepage:
                docs_url = repo.homepage
            
            license_name = repo.license.name if repo.license else "No license"
            
            if days_since_commit < 30:
                activity_status = "Very Active"
            elif days_since_commit < 90:
                activity_status = "Active"
            elif days_since_commit < 180:
                activity_status = "Moderately Active"
            elif days_since_commit < 365:
                activity_status = "Low Activity"
            else:
                activity_status = "Inactive"
            
            info = f"""Repository: {repo.full_name} Description: {repo.description or 'No description provided'} URL: {repo.html_url} 
            Created: {created_at.strftime('%Y-%m-%d')} Age: {age_years} years Primary Language: {primary_language}
            Stars: {repo.stargazers_count:,} Forks: {repo.forks_count:,} Watchers: {repo.watchers_count:,} Total Commits: {commit_count}
            Last Commit: {last_commit_date} ({days_since_commit} days ago) Activity Status: {activity_status} Contributors: {total_contributors}
            Open Issues: {repo.open_issues_count} License: {license_name} Is Fork: {'Yes' if repo.fork else 'No'} Is Archived: {'Yes' if repo.archived else 'No'}
            Documentation: {docs_url} Default Branch: {repo.default_branch}"""
            
            return info
            
        except Exception as e:
            return f"Error fetching basic info: {str(e)}"
    
    def get_issues_summary(self) -> str:
        """Get a summary of open issues including count and whether any are critical. 
        Returns a formatted string with open issue count and critical issue indicators."""

        try:
            repo = self._get_repo_info()
            
            open_issue_count = repo.open_issues_count
            
            if open_issue_count == 0:
                return "No open issues."
            
            critical_count = 0
            bug_count = 0
            issues_checked = 0
            
            for issue in repo.get_issues(state='open', sort='created', direction='desc'):
                if issue.pull_request: 
                    continue
                    
                issues_checked += 1
                if issues_checked > 10:
                    break
                
                label_names = [label.name.lower() for label in issue.labels]
                if any(keyword in ' '.join(label_names) for keyword in ['critical', 'urgent', 'blocker', 'high-priority', 'severity-high']):
                    critical_count += 1
                if 'bug' in label_names:
                    bug_count += 1
            
            result = f"Open Issues: {open_issue_count}"
            if critical_count > 0:
                result += f"\nCritical/Urgent Issues: {critical_count} (check recent issues)"
            if bug_count > 0:
                result += f"\nBug Issues: {bug_count}"
            
            return result
            
        except Exception as e:
            return f"Error fetching issues summary: {str(e)}"
    
    def get_top_contributors(self) -> str:
        """Get the top 5 contributors to the repository by commit count. Returns a formatted 
        string with top contributor usernames and their contribution counts."""

        try:
            repo = self._get_repo_info()
            count = 5
            contributors = list(repo.get_contributors()[:count])
            
            if not contributors:
                return "No contributor data available."
            
            result = f"Top {len(contributors)} Contributors:"
            for i, contributor in enumerate(contributors, 1):
                result += f"\n  {i}. {contributor.login}: {contributor.contributions} contributions"
            
            return result
            
        except Exception as e:
            return f"Error fetching contributors: {str(e)}"

