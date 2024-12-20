from github import Github
import datetime, time
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import tqdm
import pickle
import os
import sqlite3
import argparse

class Dashboard:

    def __init__(self, key, repo, db_file, port=5000):
        self.key = key
        self.repo_path = repo
        self.github = Github(self.key)
        self.repo = self.github.get_repo(self.repo_path)
        self.app = Flask(__name__)
        self.app.add_url_rule(
            "/webhook", "webhook", self.handle_webhook, methods=["POST"]
        )
        self.db_file = db_file
        self.port = port

    def start(self):
        self.app.run(port=self.port, debug=True)

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
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("PRAGMA busy_timeout = 5000;")
        print("ADDING COMMIT")
        branch_name = data.get("ref").replace("refs/heads/", "")
        pusher = data.get("pusher", {}).get("name")
        for commit in data.get("commits", []):
            commit_hash = commit.get("id")
            author = data.get("author", {}).get("name")
            message = commit.get("message")
            c.execute(
                "INSERT OR REPLACE INTO commits (hash, author, message) VALUES (?, ?, ?)",
                (commit_hash, author, message),
            )
        conn.commit()
        conn.close()

    def add_branch(self, data):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("PRAGMA busy_timeout = 5000;")
        print("ADDING BRANCH")
        branch_name = data.get("ref")
        author = data.get("sender", {}).get("login")
        c.execute(
            "INSERT OR REPLACE INTO branches (name, author) VALUES (?, ?)",
            (branch_name, author),
        )
        conn.commit()
        conn.close()

    def add_workflow_run(self, data):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("PRAGMA busy_timeout = 5000;")
        print("ADDING WORKFLOW RUN")
        workflow_run = data.get("workflow_run", {})
        workflow_name = workflow_run.get("name")
        branch_name = workflow_run.get("head_branch")
        commit_hash = workflow_run.get("head_sha")
        author = workflow_run.get("actor", {}).get("login")
        conclusion = workflow_run.get("conclusion")
        status = workflow_run.get("status")
        run_id = workflow_run.get("id")
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
            queue_time = (started_at_dt - created_at_dt).total_seconds()
        else:
            queue_time = (updated_at_dt - created_at_dt).total_seconds()
        created_at = time.mktime(created_at_dt.timetuple())
        updated_at = time.mktime(updated_at_dt.timetuple())
        started_at = time.mktime(started_at_dt.timetuple())
        c.execute("SELECT id FROM branches WHERE name = ?", (branch_name,))
        try:
            branch_id = c.fetchone()[0]
        except:
            print(f"No branch id found for {branch_name}")
            branch_id = -1
        c.execute("SELECT id FROM commits WHERE hash = ?", (commit_hash,))
        try:
            commit_id = c.fetchone()[0]
        except:
            print(f"No commit id found for {commit_hash}")
            commit_id = -1
        c.execute("SELECT id FROM workflows WHERE name = ?", (workflow_name,))
        try:
            workflow_id = c.fetchone()[0]
        except:
            print(f"No workflow id found for {workflow_name}")
            workflow_id = -1
        c.execute(
            "INSERT OR REPLACE INTO workflowruns (branch, commitid, workflow, author, runtime, createtime, starttime, endtime, queuetime, status, conclusion, url, gitid, archivedbranchname, archivedcommithash, archivedworkflowname) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                branch_id,
                commit_id,
                workflow_id,
                author,
                runtime,
                created_at,
                started_at,
                updated_at,
                queue_time,
                status,
                conclusion,
                run_url,
                run_id,
                branch_name,
                commit_hash,
                workflow_name,
            ),
        )
        conn.commit()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Backend-Listener",
                                     description="starts the listener to live update the database")
    parser.add_argument('-db', '--database', help="database file in .db format")
    parser.add_argument('-r', '--repo', help="repository to scrape data from")
    parser.add_argument('-k', "--key", help="repository key")
    parser.add_argument('-p', "--port", help="port to expose", default=5000)
    args = parser.parse_args()
    dashboard = Dashboard(
        args.key,
        args.repo,
        args.database,
        args.port
    )
    dashboard.start()