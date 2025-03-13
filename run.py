import sqlite3
import config;
from utils.contracts import requires, ensures;

import sys ;

from databaseIOManager import objDatabaseInterface; 

import time;

objDatabaseInterface.open();

import os ;
import traceback; 

objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Starting run.py."]);
print(str(list(objDatabaseInterface.cursor.execute("SELECT * FROM RunLogsTable"))));
objDatabaseInterface.connection.commit();

try:
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
