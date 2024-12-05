from github import Github
import datetime
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

class Dashboard:

    def __init__(self, key, repo):
        self.key = key
        self.repo_path = repo
        self.github = Github(self.key)
        self.repo = self.github.get_repo(self.repo_path)
        self.app = Flask(__name__)
        self.app.add_url_rule('/webhook', 'webhook', self.handle_webhook, methods=["POST"])
        self.stats = {}
        self.init_stats()

    def start(self):
        self.app.run(port=5000, debug=True)

    def stop(self):
        pass

    def init_stats(self):
        branches = self.repo.get_branches()
        workflows = self.repo.get_workflows()
        for branch in branches:
            self.stats[branch.name] = pd.DataFrame(columns = ["name", "status", "conclusion", "run-time", "queue-time"])
            for workflow in workflows:
                workflow_runs = workflow.get_runs(branch=branch.name)
                try:
                    most_recent_run = workflow_runs[0]
                    new_row = {"name": most_recent_run.name, 
                            "status": most_recent_run.status, 
                            "conclusion": most_recent_run.conclusion,
                            "run-time": (most_recent_run.updated_at - most_recent_run.created_at),
                            "queue-time": (most_recent_run.run_started_at - most_recent_run.created_at)}
                    existing_index = self.stats[branch.name][self.stats[branch.name]["name"] == new_row["name"]].index
                    #This if statement allows for different behavior based on whenter the run is the most recent or not
                    # currrently there is no difference in behavior
                    if not existing_index.empty:
                        #self.stats[branch.name].loc[existing_index[0]] = new_row
                        self.stats[branch.name].loc[len(self.stats[branch.name])] = new_row
                    else:
                        self.stats[branch.name].loc[len(self.stats[branch.name])] = new_row
                except IndexError:
                    print(f"workflow {workflow.name} has never been run in branch {branch.name}")


    def get_new_stats(self, branch, workflow):
        workflow_object = next(w for w in self.repo.get_workflows() if w.name == workflow)
        workflow_runs = workflow_object.get_runs(branch=branch)
        new_row = {}
        if workflow_runs.totalCount > 0:
            most_recent_run = workflow_runs[0]
            new_row['name'] = most_recent_run.name
            new_row['status'] = most_recent_run.status
            new_row['conclusion'] = most_recent_run.conclusion
            new_row['run-time'] = most_recent_run.updated_at - most_recent_run.created_at
            new_row['queue-time'] = most_recent_run.run_started_at - most_recent_run.created_at
            
        else:
            print("No workflows found")
        return new_row

    def handle_webhook(self):
        data = request.get_json()
        if data.get('action') == 'completed' and 'workflow_run' in data:
            print("STARTING")
            branch = data['workflow_run']['head_branch']
            workflow_name = data['workflow_run']['name']
            new_row = self.get_new_stats(branch, workflow_name)
            print(new_row)
            if new_row["conclusion"] == "failure":
                print(f"Warning!!!, {workflow_name} failed on branch {branch}")
            existing_index = self.stats[branch][self.stats[branch]["name"] == new_row["name"]].index
            if not existing_index.empty:
                #self.stats[branch].loc[existing_index[0]] = new_row
                self.stats[branch].loc[len(self.stats[branch])] = new_row
            else:
                self.stats[branch].loc[len(self.stats[branch])] = new_row
            print(self.stats[branch])
        return '', 200
            

if __name__ == "__main__":
    dashboard = Dashboard("insert token here", "Eliasj42/iree")
    dashboard.start()



    