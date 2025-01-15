# Dashboard Backend

This code works as a backend to listen for changes to monitered repositories and update the database underlying the dashboard.

## Step 1: Initialization

to initialize the backend database, run the `local-database.py` script with the following arguments:

`-db`: the database file you want to write to.  It should have the suffix `.db` and should not already exist.  If it does already exist, remove it first

`-r`: the repo you want to pull from, should be in the format `'iree-org/iree'`

`-k`: the key that gives permissions to pull data from that repository 

`-m`: the max number of workflows to scrape. You might want to set this for larger repositories

`-i`: Initialize. use this if you want to reset the `.db`. 

The full command should look like this
```
python local-database.py -db /home/user/dashboard-test/ml-compiler-build-dashboards/demo/iree-repo.db -r "iree-org/iree" -k "ghp_putyourkeyhere"
```

##Step 2: Listener

To run the listener, you need the same arguments as above, except there is an optional `-p` port argument. if no port is given, it will use `5000`. There is also ni optional `-i` or `-m` flags

Make sure that that port is exposed, and that the url it is exposed on is in a webhook in the repository you are monitering, otherwise it will not recieve live updates

The full command should look like this:
```
python listener.py -db /home/user/dashboard-test/ml-compiler-build-dashboards/demo/iree-repo.db -r "iree-org/iree" -k "ghp_putyourkeyhere" -p 5000
```
## Step 3: Using the backend

The listener will constantly update the `.db` file provided.  to get data for visualizations or analysis, use the `sqlite3` package and query the `.db` file.

# Maintenance

If the Listener ever goes down, you can just reuse the same command you used to start it to restart it.

If it has been down for a while, you can use the `local-database.py` script without the `-i` flag and a low `-m` flag