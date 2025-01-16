# Dashboard Backend

This code works as a backend to listen for changes to monitered repositories and update the database underlying the dashboard.

# Using the backend

If you are not maintaining the backend, you can access and query the database by using the connector object defined in sqlauthenticator.py
```
from sqlauthenticator import connector
conn = connector(password)
```
from here conn can be used like an sqlite3 connector.  Be sure to close it when you are finished querying if your script runs for a while to avoid locking out the listener

# Initializing the backend 

to initialize the backend database, run the `local-database.py` script with the following arguments:


`-r`: the repo you want to pull from, should be in the format `'iree-org/iree'`

`-k`: the key that gives permissions to pull data from that repository 

`-m`: the max number of workflows to scrape. You might want to set this for larger repositories

`-pwd`: The password to the Azure Database

The full command should look like this
```
python local-database.py -r "iree-org/iree" -k "your key here" -m 1000 -pwd password
```

##Step 2: Listener

To run the listener, you need the same arguments as above, except there is an optional `-p` port argument. if no port is given, it will use `5000`. There is also no optional `-m` flag

Make sure that that port is exposed, and that the url it is exposed on is in a webhook in the repository you are monitering, otherwise it will not recieve live updates

The full command should look like this:
```
python listener.py -r "iree-org/iree" -k "ghp_putyourkeyhere" -p 5000 -pwd password
```


# Maintenance

If the Listener ever goes down, you can just reuse the same command you used to start it to restart it.

If it has been down for a while, you can use the `local-database.py` script without the `-i` flag and a low `-m` flag