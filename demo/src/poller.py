
# app/poller.py
import asyncio
from datetime import datetime
from .database import SessionLocal
from github_client import GitHubClient
from .models import Workflow, Job, StatusEnum

class WorkflowPoller:
    def __init__(self, github_token: str, poll_interval: int = 60):
        self.github_client = GitHubClient(github_token)
        self.poll_interval = poll_interval

    async def poll_workflows(self):
        while True:
            try:
                workflows = await self.github_client.get_workflow_runs("pytorch", "pytorch")
                self._update_database(workflows)
            except Exception as e:
                print(f"Error polling workflows: {e}")
            await asyncio.sleep(self.poll_interval)

    def _update_database(self, workflows):
        db = SessionLocal()
        try:
            for workflow_data in workflows["workflow_runs"]:
                workflow = db.query(Workflow).filter_by(id=workflow_data["id"]).first()
                if not workflow:
                    workflow = Workflow(
                        id=workflow_data["id"],
                        name=workflow_data["name"],
                        branch=workflow_data["head_branch"],
                        commit=workflow_data["head_sha"],
                        author=workflow_data["actor"]["login"],
                        status=self._map_github_status(workflow_data["status"]),
                        start_time=datetime.fromisoformat(workflow_data["created_at"].replace("Z", "+00:00")),
                        duration=self._calculate_duration(workflow_data["created_at"])
                    )
                    db.add(workflow)
                db.commit()
        finally:
            db.close()

    def _map_github_status(self, status: str) -> StatusEnum:
        status_mapping = {
            "completed": StatusEnum.SUCCESS,
            "in_progress": StatusEnum.RUNNING,
            "queued": StatusEnum.PENDING,
            "failed": StatusEnum.FAILED
        }
        return status_mapping.get(status, StatusEnum.WARNING)

    def _calculate_duration(self, start_time: str) -> str:
        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        duration = datetime.utcnow() - start
        return f"{int(duration.total_seconds() / 60)}m"
