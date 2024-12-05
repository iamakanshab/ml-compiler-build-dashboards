import requests
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        self.base_url = "https://api.github.com"

    def get_workflow_runs(self, owner: str, repo: str, branch: Optional[str] = None) -> List[dict]:
        """
        Fetch recent workflow runs from GitHub Actions
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs"
        params = {'branch': branch} if branch else {}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get('workflow_runs', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflow runs: {e}")
            return []

    def get_workflow_jobs(self, owner: str, repo: str, run_id: int) -> List[dict]:
        """
        Fetch jobs for a specific workflow run
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json().get('jobs', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflow jobs: {e}")
            return []