import sqlite3
import config;
from utils.contracts import requires, ensures;

import subprocess;

import sys ;

from databaseIOManager import objDatabaseInterface; 

import time;

objDatabaseInterface.open();

import os ;
import traceback; 

objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Starting run.py."]);
objDatabaseInterface.connection.commit();



def getRunContent():
    dictToWrite=dict();
    for command in [ ['id'], ['hostname'], ['cat', '/etc/machine-id'], ['pwd']]:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if( len(stderr) > 0 or ((process.returncode) is not None and (process.returncode != 0)) ):
            raise Exception(
                "The following error occurred while gathering information about the running content using commmand"+ \
                str(command)+":\n    "+stderr.replace("\n", "\n    ") \
                );
        dictToWrite[str(command)] = stdout;
    return str(dictToWrite);




try:

    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Run context information:" + getRunContent()]);
    objDatabaseInterface.connection.commit();
 


    cycleNumber=0;
    while(True):
        # objDatabaseInterface.cursor.execute("BEGIN");
        objDatabaseInterface.connection.rollback();
        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
            [f"Starting Loop Cycle Number {cycleNumber} of this execution of the daemon"]);
        objDatabaseInterface.connection.commit();

        if( os.path.exists(config.defaultValues.nameOfFileToCauseDaemonToExit) ):
            objDatabaseInterface.connection.rollback();
            objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
                [f"Detected the existance of the flagging-file used to command this daemon to exist, \"{config.defaultValues.nameOfFileToCauseDaemonToExit}\""]);
            objDatabaseInterface.connection.commit();
            break;    

        try:
            print("hi!");
        except:
            print("oh no");

        objDatabaseInterface.connection.rollback();
        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
            [f"Ending Loop Cycle Number {cycleNumber} of this execution of the daemon. "+\
             f"Proceeding to sleep for {config.defaultValues.timeToSleepBetweenChecks} seconds after committing this."]);
        objDatabaseInterface.connection.commit();

        cycleNumber=cycleNumber+1;

        time.sleep(config.defaultValues.timeToSleepBetweenChecks);

except: # The item to the right does not work as hoped to catch KeyboadInterupts it seems...#  Exception as e:
    objDatabaseInterface.connection.rollback();
    errorMessageIndented = "    " + "".join(traceback.format_exc()).replace("\n", "\n    ");
    # exceptionAsStringIndented=str(e).replace("\n", "\n    ");
    stringToPrint="An exception has occurred (note: keyboard interupts have the nasty tendency of leaving the trace empty). Details:\nTraceback:\n{errorMessageIndented}"; # \nException e:\n{exceptionAsStringIndented}";
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
        [stringToPrint]);
    objDatabaseInterface.connection.commit();    
    sys.stderr.write(stringToPrint);
    sys.stderr.flush();
    

objDatabaseInterface.connection.rollback();
objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Preparing to exit run.py: Making final commit then closing connection."]);
objDatabaseInterface.connection.commit();
objDatabaseInterface.connection.rollback();    
objDatabaseInterface.close();
