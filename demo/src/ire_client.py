from github import Github
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class IREEClient:
    def __init__(self, repo_name="openxla/iree"):
        self.repo_name = repo_name
        # Initialize without token for public repo access
        self.github = Github()
        self.repo = self.github.get_repo(repo_name)

    def get_recent_workflows(self, hours=24):
        """Fetch recent workflow runs"""
        try:
            workflows = []
            for workflow in self.repo.get_workflows():
                runs = workflow.get_runs()
                for run in runs:
                    if datetime.now() - run.created_at < timedelta(hours=hours):
                        workflows.append({
                            'name': workflow.name,
                            'status': run.status,
                            'conclusion': run.conclusion,
                            'branch': run.head_branch,
                            'timestamp': run.created_at,
                            'run_time': (run.updated_at - run.created_at).total_seconds() / 60 if run.updated_at else None
                        })
            logger.info(f"Fetched {len(workflows)} recent workflows")
            return workflows
        except Exception as e:
            logger.error(f"Error fetching workflows: {e}")
            return []

    def get_build_metrics(self):
        """Calculate build metrics from recent runs"""
        try:
            runs = list(self.repo.get_workflow_runs())
            recent_runs = [r for r in runs if datetime.now() - r.created_at < timedelta(hours=24)]
            
            failed = len([r for r in recent_runs if r.conclusion == 'failure'])
            total = len(recent_runs)
            
            return {
                'total_builds_24h': total,
                'failed_builds_24h': failed,
                'success_rate': round(((total - failed) / total * 100), 1) if total > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {
                'total_builds_24h': 0,
                'failed_builds_24h': 0,
                'success_rate': 0
            }