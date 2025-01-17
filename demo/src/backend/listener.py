from github import Github
import datetime, time
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import tqdm
import pickle
import os
import argparse
from sqlauthenticator import connector

class Dashboard:

    def __init__(self, key, repo, password, port=5000):
        self.key = key
        self.repo_path = repo
        self.github = Github(self.key)
        self.repo = self.github.get_repo(self.repo_path)
        self.password = password
        self.app = Flask(__name__)
        self.app.add_url_rule(
            "/webhook", "webhook", self.handle_webhook, methods=["POST"]
        )
        self.port = port

    def start(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=True)

    def stop(self):
        pass

    def handle_webhook(self):
        data = request.get_json()
        # handle new branch creation
        if data.get("ref_type") == "branch":
            self.add_branch(data)
        # handle new commit
        if "commits" in data:
            self.add_commit(data)
        # handle new workflow run
        if "workflow_run" in data:
            self.add_workflow_run(data)
        return "", 200

    def add_commit(self, data):
        conn = connector(self.password)
        c = conn.cursor()
        print("ADDING COMMIT")
        branch_name = data.get("ref").replace("refs/heads/", "")
        pusher = data.get("pusher", {}).get("name")
        for commit in data.get("commits", []):
            commit_hash = commit.get("id")
            try:
                author = data.get("author", {}).get("name")
                commit_time = data.get("author, {}").get("date")
            except:
                print(f"No Author found for {commit_hashj}")
            message = commit.get("message")
            commit_time = time.mktime(commit_time.timetuple())
            c.execute(
                """
                MERGE INTO commits AS target
                USING (VALUES (?, ?, ?, ?, ?)) AS source (hash, author, message, time, repo)
                ON target.hash = source.hash
                WHEN MATCHED THEN
                    UPDATE SET 
                        target.author = source.author, 
                        target.message = source.message, 
                        target.time = source.time, 
                        target.repo = source.repo
                WHEN NOT MATCHED BY TARGET THEN
                    INSERT (hash, author, message, time, repo) 
                    VALUES (source.hash, source.author, source.message, source.time, source.repo);
                """,
                (commit_hash, author, message, self.repo_path),
            )
        conn.commit()
        conn.close()

    def add_branch(self, data):
        conn = connector(self.password)
        c = conn.cursor()
        print("ADDING BRANCH")
        branch_name = data.get("ref")
        author = data.get("sender", {}).get("login")
        c.execute(
            """
            MERGE INTO branches AS target
            USING (VALUES (?, ?)) AS source (name, repo)
            ON target.name = source.name
            WHEN MATCHED THEN
                UPDATE SET target.repo = source.repo
            WHEN NOT MATCHED BY TARGET THEN
                INSERT (name, repo) VALUES (source.name, source.repo);
            """,
            (branch_name, author, self.repo_path),
        )
        conn.commit()
        conn.close()

    def add_workflow_run(self, data):
        conn = connector(self.password)
        c = conn.cursor()
        print("ADDING WORKFLOW RUN")
        workflow_run = data.get("workflow_run", {})
        workflow_name = workflow_run.get("name")
        branch_name = workflow_run.get("head_branch")
        commit_hash = workflow_run.get("head_sha")
        author = workflow_run.get("actor", {}).get("login")
        conclusion = workflow_run.get("conclusion")
        status = workflow_run.get("status")
        gitid = workflow_run.get("id")
        run_url = workflow_run.get("html_url")
        created_at_dt = datetime.datetime.fromisoformat(
            workflow_run.get("created_at").replace("Z", "")
        )
        updated_at_dt = datetime.datetime.fromisoformat(
            workflow_run.get("updated_at").replace("Z", "")
        )
        started_at_dt = datetime.datetime.fromisoformat(
            workflow_run.get("run_started_at").replace("Z", "")
        )
        try:
            runtime = workflow_run.timing().run_duration_ms / 100
        except:
            runtime = (updated_at_dt - started_at_dt).total_seconds()
        if status == "queued":
            queue_time = (updated_at_dt - created_at_dt).total_seconds()
        else:
            queue_time = (started_at_dt - created_at_dt).total_seconds()
        c.execute(
            """
            MERGE INTO workflowruns AS target
            USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) 
            AS source (gitid, author, runtime, createtime, starttime, endtime, queuetime, status, conclusion, url, branchname, commithash, workflowname, repo)
            ON target.gitid = source.gitid
            WHEN MATCHED THEN
                UPDATE SET 
                    target.author = source.author,
                    target.runtime = source.runtime,
                    target.createtime = source.createtime,
                    target.starttime = source.starttime,
                    target.endtime = source.endtime,
                    target.queuetime = source.queuetime,
                    target.status = source.status,
                    target.conclusion = source.conclusion,
                    target.url = source.url,
                    target.branchname = source.branchname,
                    target.commithash = source.commithash,
                    target.workflowname = source.workflowname,
                    target.repo = source.repo
            WHEN NOT MATCHED BY TARGET THEN
                INSERT (gitid, author, runtime, createtime, starttime, endtime, queuetime, status, conclusion, url, branchname, commithash, workflowname, repo) 
                VALUES (source.gitid, source.author, source.runtime, source.createtime, source.starttime, source.endtime, source.queuetime, source.status, source.conclusion, source.url, source.branchname, source.commithash, source.workflowname, source.repo);
            """,
            (
                gitid,
                author,
                runtime,
                created_at_dt,
                started_at_dt,
                updated_at_dt,
                queue_time,
                status,
                conclusion,
                run_url,
                branch_name,
                commit_hash,
                workflow_name,
                self.repo_path
            ),
        )
        conn.commit()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Backend-Listener",
                                     description="starts the listener to live update the database")
    parser.add_argument('-r', '--repo', help="repository to scrape data from")
    parser.add_argument('-k', "--key", help="repository key")
    parser.add_argument('-p', "--port", help="port to expose", default=5000)
    parser.add_argument('-pwd', '--password', help="Password to remote database")
    args = parser.parse_args()
    dashboard = Dashboard(
        args.key,
        args.repo,
        args.password,
        args.port
    )
    dashboard.start()