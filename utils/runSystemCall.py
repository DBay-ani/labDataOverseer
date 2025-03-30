from utils.contracts import requires, ensures;

import subprocess;

from databaseIOManager import objDatabaseInterface; 


def runSystemCall(command):
    # Commit database state prior to calling this.... would be nice to make a sub-transaction if one code with
    # what Sqlite3 and the Python setup allow...
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if( len(stderr) > 0 or ((process.returncode) is not None and (process.returncode != 0)) ):
        errorString=(
            f"The following error occurred while running the system call {runSystemCall}"+ \
            str(command)+":\n    "+str(stderr).replace("\n", "\n    ") \
            );
        objDatabaseInterface.connection.rollback();
        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", [errorString]); 
        objDatabaseInterface.connection.commit();
        raise Exception(errorString);

    return stdout;

"""def recordRunContext():
    objDatabaseInterface.connection.rollback();
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Gathering process context information at start of run."); 
    objDatabaseInterface.connection.commit();


    dictToWrite=dict();
    for command in [ ['id'], ['hostname'], ['cat', '/etc/machine-id'], ['pwd'], ['git', 'status'], ['git', 'log', '-n1'], ['env'], ['git', 'diff', 'HEAD']]:
        stdout=runSystemCall(command);
        contextKey=repr(command);
        contextValue=str(stdout);

        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (contextKey, contextValue) VALUES (?, ?)", [contextKey, contextValue]); 
        objDatabaseInterface.connection.commit();

    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Done gathering process context information at start of run."); 
    objDatabaseInterface.connection.commit();
        
    return;
"""
