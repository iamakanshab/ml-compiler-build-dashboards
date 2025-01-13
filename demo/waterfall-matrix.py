import numpy as np
import sqlite3
import datetime, time
from colorama import Fore, Back, Style
import re
import argparse

def find_last_main_push(c):
    c.execute("SELECT archivedcommithash, author, status, conclusion, starttime FROM workflowruns WHERE archivedworkflowname = 'Push on main' ORDER BY endtime DESC LIMIT 1")
    results = c.fetchall()
    return results

parser = argparse.ArgumentParser(prog="waterfall",
                                     description="show history of build failures")
parser.add_argument('-db', '--database', help="database file in .db format")
args = parser.parse_args()
DBFILE = args.database

conn = sqlite3.connect(DBFILE)
c = conn.cursor()

all_chashes = find_last_main_push(c)
print(f'last push on main {all_chashes[0][0]} by {all_chashes[0][1]} {(time.mktime(datetime.datetime.now().timetuple()) - all_chashes[0][4]) / 60} minutes ago was a {all_chashes[0][3]}')

c.execute("SELECT * FROM commits ORDER BY time DESC")
commits = c.fetchall()
commit_hashes = [(commits[i][1], commits[i][2], commits[i][3]) for i in range(10000)]
workflow_runs_monitered = ['Push on main', 'PkgCI', 'CI', 'samples', 'CI - Windows x64 MSVC', 'Publish Website', 'CI - Linux arm64 clang']
results = []
for commit, _, _ in commit_hashes:
    for workflow_run in workflow_runs_monitered:
        c.execute("SELECT archivedcommithash, author, conclusion, status, archivedworkflowname, archivedbranchname FROM workflowruns WHERE archivedcommithash = ? AND archivedworkflowname = ? ORDER BY createtime DESC LIMIT 1", (commit, workflow_run))
        result = c.fetchall()
        if result != []:
            results.append(result)
conn.close()

results_dict = {"success": "0", "failure": "X", "other": "?", "cancelled": "-"}

print(workflow_runs_monitered)

def find_status(results, hash, run_name):
    for result in results:
        if result[0][0] == hash and result[0][4] == run_name:
            if result[0][2] is not None:
                return result[0][2]
    return "other"

def add_colors(statuses):
    new_statuses = ""
    for status in statuses:
        if status == "0":
            new_statuses += (Fore.GREEN + status + Style.RESET_ALL + "  ")
        elif status =="X":
            new_statuses += (Fore.RED + status + Style.RESET_ALL + "  ")
        elif status =="-":
            new_statuses += (Fore.RED + status + Style.RESET_ALL + "  ")
        else:
            new_statuses += (Fore.YELLOW + status + Style.RESET_ALL + "  ")
    return new_statuses

printed_commits = 0
for commit, chash, message in commit_hashes:
    if len(message) > 50:
        message = message[:49]
    statuses = [results_dict[find_status(results, commit, workflow_run_name)] for workflow_run_name in workflow_runs_monitered]
    if "?" not in statuses:
        print(commit[:6] + " " + chash.ljust(20) + "   " +  re.sub("\n", " ", message).ljust(50) + " " +  str(add_colors(statuses)))
        printed_commits += 1
    if printed_commits > 50: break

    
        