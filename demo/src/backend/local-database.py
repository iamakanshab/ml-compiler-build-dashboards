import sqlite3
import os
from github import Github
import datetime, time
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Local-Database",
                                     description="Initialize Local DataBase")
    parser.add_argument('-db', '--database', help="database file in .db format")
    parser.add_argument('-r', '--repo', help="repository to scrape data from")
    parser.add_argument('-k', "--key", help="repository key")
    args = parser.parse_args()
    conn = sqlite3.connect(args.database)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")

    c.execute(
        """
            CREATE TABLE branches (
                id INTEGER PRIMARY KEY, --Auto-incrementing primary key
                name TEXT UNIQUE NOT NULL,
                author TEXT
            )
            """
    )
    conn.commit()

    c.execute(
        """
            CREATE TABLE commits (
                id INTEGER PRIMARY KEY, --Auto-incrementing primary key
                hash TEXT UNIQUE NOT NULL,
                author TEXT,
                message TEXT
            )
            """
    )
    conn.commit()

    c.execute(
        """
            CREATE TABLE workflows (
                id INTEGER PRIMARY KEY, --Auto incrementing primary key
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL
            )
            """
    )
    conn.commit()

    c.execute(
        """
            CREATE TABLE workflowruns (
                id INTEGER PRIMARY KEY, --Auto incrementing primary key 
                branch INTEGER NOT NULL, --Foreign key column
                commitid INTEGER NOT NULL, --Foreign key column
                workflow INTEGER NOT NULL, --Foreign key column
                author TEXT,
                runtime REAL DEFAULT 0.0,
                createtime REAL,
                starttime REAL,
                endtime REAL,
                queuetime REAL DEFAULT 0.0,
                status TEXT,
                conclusion TEXT,
                url TEXT,
                gitid INT UNIQUE,
                archivedbranchname TEXT,
                archivedcommithash TEXT,
                archivedworkflowname TEXT
            )
            """
    )
    conn.commit()

    print("POPULATING DATABASE")
    github = Github(args.key)
    repo = github.get_repo(args.repo)


    def get_workflow_run_row(workflow_run, c):
        branch = workflow_run.head_branch
        c.execute("SELECT id FROM branches WHERE name = ?", (branch,))
        try:
            branch_id = c.fetchone()[0]
        except:
            print(f"No branch id found for {branch}")
            branch_id = -1
        commit = workflow_run.head_sha
        c.execute("SELECT id FROM commits WHERE hash = ?", (commit,))
        try:
            commit_id = c.fetchone()[0]
        except:
            print(f"No commit id found for {commit}")
            commit_id = -1
        workflow_name = workflow_run.name
        c.execute("SELECT id FROM workflows WHERE name = ?", (workflow_name,))
        try:
            workflow_id = c.fetchone()[0]
        except:
            print(f"No workflow id found for {workflow_name}")
            workflow_id = -1
        url = workflow_run.url
        gitid = workflow_run.id
        author = workflow_run.actor.login
        status = workflow_run.status
        conclusion = workflow_run.conclusion
        createtime = time.mktime(workflow_run.created_at.timetuple())
        starttime = time.mktime(workflow_run.run_started_at.timetuple())
        endtime = time.mktime(workflow_run.updated_at.timetuple())
        if staus != "queued":
            queuetime = starttime - createtime
        else:
            queuetime = endtime - createtime
        try:
            runtime = workflow_run.timing().run_duration_ms / 100
        except:
            runtime =  endtime - starttime
        return (
            branch_id,
            commit_id,
            workflow_id,
            author,
            runtime,
            createtime,
            starttime,
            endtime,
            queuetime,
            status,
            conclusion,
            url,
            gitid,
            branch,
            commit,
            workflow_name,
        )


    print("POPULATING BRANCHES")

    branches = repo.get_branches()
    branch_values = [(branch.name,) for branch in branches]
    c.executemany(
        "INSERT OR REPLACE INTO branches (name) VALUES (?)", branch_values
    )
    conn.commit()

    print("POPULATING COMMITS")

    commits = repo.get_commits()
    commit_values = [
        (str(commit.sha), commit.commit.author.name, commit.commit.message)
        for commit in commits
    ]
    c.executemany(
        "INSERT OR REPLACE INTO commits (hash, author, message) VALUES (?, ?, ?)",
        commit_values,
    )
    conn.commit()

    print("POPULATING WORKFLOWS")

    workflows = repo.get_workflows()
    workflow_values = [(workflow.name, workflow.url) for workflow in workflows]
    c.executemany(
        "INSERT OR REPLACE INTO workflows (name, url) VALUES (?, ?)",
        workflow_values,
    )
    conn.commit()

    print("POPULATING WORKFLOW RUNS")

    workflow_runs = repo.get_workflow_runs()
    workflow_run_values = []
    i = 0
    for workflow_run in workflow_runs:
        print(i)
        if i > 1_000: break
        workflow_run_values.append(get_workflow_run_row(workflow_run, c))
        i += 1
    c.executemany(
        "INSERT OR REPLACE INTO workflowruns (branch, commitid, workflow, author, runtime, createtime, starttime, endtime, queuetime, status, conclusion, url, gitid, archivedbranchname, archivedcommithash, archivedworkflowname) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        workflow_run_values,
    )
    conn.commit()

    if __name__ == "__main__":
        print("TESTING DB")

    conn.commit()
    conn.close()
