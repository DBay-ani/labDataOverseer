import sqlite3
import config;
from utils.contracts import requires, ensures;

import subprocess;

import sys ;

from databaseIOManager import objDatabaseInterface; 

import time;


import os ;
import traceback; 

from utils.handleError import handleError;

thisFileName=(__file__.split("/")[-1]);

objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", [f"Starting `{thisFileName}` ."]);
objDatabaseInterface.connection.commit();



#TODO: add code to clean the received/processed-message folder every so often...
def testFunct(*x) -> None:
    print("Starting test funct",flush=True);
    time.sleep(30);
    print("Exitting test funct", flush=True);

routinesToCallAndTheirName=[ \
    (testFunct,"ExampleFunction")
];


try:


    cycleNumber=0;
    while(True):
        print(f"{cycleNumber}",flush=True);
        # objDatabaseInterface.cursor.execute("BEGIN");
        objDatabaseInterface.connection.rollback();
        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
            [f"Starting Loop Cycle Number {cycleNumber} of this execution of the `{thisFileName}`."]);
        objDatabaseInterface.connection.commit();

        if( os.path.exists(config.defaultValues.nameOfFileToCauseDaemonToExit) ):
            objDatabaseInterface.connection.rollback();
            objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
                [f"Detected the existance of the flagging-file used to command this `{thisFileName}` to exit, \"{config.defaultValues.nameOfFileToCauseDaemonToExit}\""]);
            objDatabaseInterface.connection.commit();
            break;    

        for thisSubRoutine, subRoutineName in routinesToCallAndTheirName:
            objDatabaseInterface.connection.rollback();
            objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
                [f"Starting execution of subroutine \"{subRoutineName}\"."]);
            objDatabaseInterface.connection.commit();

            try:
                thisSubRoutine(objDatabaseInterface);
            except:
                handleError(f"An exception has occurred while running subroutine {subRoutineName}");

        objDatabaseInterface.connection.rollback();
        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
            [f"Ending Loop Cycle Number {cycleNumber} of this execution of `{thisFileName}`. "+\
             f"Proceeding to sleep for {config.defaultValues.timeToSleepBetweenChecks} seconds after committing this."]);
        objDatabaseInterface.connection.commit();

        cycleNumber=cycleNumber+1;

        time.sleep(config.defaultValues.timeToSleepBetweenChecks);

except: # The item to the right does not work as hoped to catch KeyboadInterupts it seems...#  Exception as e:
    handleError(f"An exception has occurred that has been handled by the top-level of `{thisFileName}` " + \
                "(note: keyboard interupts have the nasty tendency of leaving the trace empty).");

    

objDatabaseInterface.connection.rollback();
objDatabaseInterface.cursor.execute(f"INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
    [f"Preparing to exit `{thisFileName}`; Making final commit then closing connection."]);
objDatabaseInterface.connection.commit();
objDatabaseInterface.connection.rollback();    
objDatabaseInterface.close();
