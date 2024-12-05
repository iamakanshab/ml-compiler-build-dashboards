# app/github_client.py
from typing import Optional
import aiohttp
import asyncio

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}" if token else None
        }

    async def get_workflow_runs(self, owner: str, repo: str):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs"
            async with session.get(url, headers=self.headers) as response:
                return await response.json()

    async def get_workflow_jobs(self, owner: str, repo: str, run_id: int):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
            async with session.get(url, headers=self.headers) as response:
                return await response.json()