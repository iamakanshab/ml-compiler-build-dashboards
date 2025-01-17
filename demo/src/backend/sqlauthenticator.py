import pyodbc

def connector(pwd):
    server = 'dashboard-backend.database.windows.net'
    database = 'dashboard-backend'
    username = 'CloudSA9134000b'
    password = pwd
    driver = '{ODBC Driver 17 for SQL Server}' 
    connection = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
    )
    return connection