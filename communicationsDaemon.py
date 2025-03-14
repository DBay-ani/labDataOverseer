import sqlite3
import config;
from utils.contracts import requires, ensures;

import subprocess;

import sys ;

from databaseIOManager import objDatabaseInterface; 

import time;


import os ;
import traceback; 

from utils.getRunContext import getRunContext ;
from utils.handleError import handleError;

thisFileName=(__file__.split("/")[-1]);

objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", [f"Starting `{thisFileName}` ."]);
objDatabaseInterface.connection.commit();


# check
# read
#    move
#    send to handler
#       if error, write error-reply
# read
# reply
#    REPLYTO: (name of the file that was put in the inbox)
#    TIME_READ: 
#    REPLY:
#        
# Considered YAML, but JSON looks better at minor cost of extra syntax
# 
# To write the sanitized file text:
# >>> import json
# >>> json.dump
# json.dump(   json.dumps(  
# >>> json.dumps("fdg ertre t\" ");
# '"fdg ertre t\\" "'
# >>> A = json.dumps("fdg ertre t\" ");
# >>> print(A)
# "fdg ertre t\" "
# >>> 
#
# For writting out replies:
#>>> print(json.dumps({1:2,3:{3.1:4.1, 3.2:4.2}, 5:6}, indent=4))
# {
#    "1": 2,
#    "3": {
#        "3.1": 4.1,
#        "3.2": 4.2
#    },
#    "5": 6
#}
#>>> 


import uuid;

def issueReply(originalFileName : str, errorDetected: bool,  contentOfReply : dict, 
     timeReceivedAsReadableString: str) -> None:

    placeToSaveReply=configs.defaultValues.directory_communication_outgoing + str(uuid.uuid4())+".json";

    fileContent=json.dumps(\
        {"REPLY_TO":originalFileName, \
         "ERROR_DETECTED":errorDetected, \
         "TIME_RECEIVED": timeReceivedAsReadableString, \ 
         "CONTENT": contentOfReply}, indent=4);
    fh=open(placeToSaveReply, "w");
    fh.write(fileContent);
    fh.close();

    objDatabaseInterface.connection.rollback();
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
        [f"Sent outgoing message \"{placeToSaveReply}\" in reply to initially received message with file name \"{originalFileName}\"."]);
    objDatabaseInterface.connection.commit();


    # TODO: save these communications in table 

def formReplyStatingErrorOccurred(fullPath : str, fileName:str, errorMessageIndented:str, timeReceivedAsReadableString:str) -> None:
    objDatabaseInterface.connection.rollback();
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
        [f"Issuing reply to received message \"{fullPath}\" indicating error occurred."]);
    objDatabaseInterface.connection.commit();

    issueReply(fileName, errorDetected=True,  contentOfReply={"ERROR_MESSAGE":errorMessageIndented}, \
        timeReceivedAsReadableString=timeReceivedAsReadableString);
 
    return; 




def handleMessage(fullPath: str, fileName : str) -> None:
    requires(fullPath.endswith(fileName));

    objDatabaseInterface.connection.rollback();
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
        [f"Starting to process received message \"{fullPath}\"."]);
    objDatabaseInterface.connection.commit();
 
    timeReceivedAsReadableString=""; # NOTE THAT THE TIME STRING COULD BE EMPTY IF SOME ERROR OCCURS WITH
                                     # TRYING TO GET THE FILE MODIFICATION TIME
    try:
        timeReceivedAsReadableString=datetime.datetime.fromtimestamp(os.stat(fullPath).st_mtime, datetime.UTC).strftime('m%Mhtw%Hd%dM%my%YtzUTC')
        # TODO: read message into memory
        # TODO: save read messages in a table, assumming they are not excessively long (check).
        # TODO: move message file
        # TODO: parse message with JSON
        # TODO: process request

    except:
        errorMessageIndented=handleError(f"Error while processing received message \"{fullPath}\".");
        formReplyStatingErrorOccurred(fullPath,fileName, errorMessageIndented, timeReceivedAsReadableString);         

    objDatabaseInterface.connection.rollback();
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
        [f"End of processing received message \"{fullPath}\"."]);
    objDatabaseInterface.connection.commit();



def readAndAddressMessages() -> None:
    for thisF in os.listdir(configs.defaultValues.directory_communication_incoming):
        if(not os.path.isfile(x)):
            continue;
        assert(os.path.exists(thisF));
        handleMessage(configs.defaultValues.directory_communication_incoming+thisF);   
    return ;





routinesToCallAndTheirName=[ \
    (readAndAddressMessage,"ReadAndAddressMessages")
];


try:

    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Run context information:" + getRunContext()]);
    objDatabaseInterface.connection.commit();
 

    cycleNumber=0;
    while(True):

        print(f"{cycleNumber}",flush=True);

        if(cycleNumber % communicationDaemon_logCycleFrequency == 0):
            # Not logging every cycle since this is expected to run far more often
            # than the other Daemon
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
            if(cycleNumber % communicationDaemon_logCycleFrequency == 0):
                # Not logging every cycle since this is expected to run far more often
                # than the other Daemon
                objDatabaseInterface.connection.rollback();
                objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
                    [f"Starting execution of subroutine \"{subRoutineName}\"."]);
                objDatabaseInterface.connection.commit();

            try:
                thisSubRoutine(objDatabaseInterface);
            except:
                handleError(f"An exception has occurred while running subroutine {subRoutineName}");

        if(cycleNumber % communicationDaemon_logCycleFrequency == 0):
            # Not logging every cycle since this is expected to run far more often
            # than the other Daemon

            objDatabaseInterface.connection.rollback();
            objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
                [f"Ending Loop Cycle Number {cycleNumber} of this execution of `{thisFileName}`. "+\
                 f"Proceeding to sleep for {config.defaultValues.timeToSleepBetweenChecks} seconds after committing this."]);
            objDatabaseInterface.connection.commit();

        cycleNumber=cycleNumber+1;

        time.sleep(config.defaultValues.timeToSleepBetweenChecks_communicationDaemon);

except: # The item to the right does not work as hoped to catch KeyboadInterupts it seems...#  Exception as e:
    handleError(f"An exception has occurred that has been handled by the top-level of `{thisFileName}` " + \
                "(note: keyboard interupts have the nasty tendency of leaving the trace empty).");

    

objDatabaseInterface.connection.rollback();
objDatabaseInterface.cursor.execute(f"INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
    [f"Preparing to exit `{thisFileName}`; Making final commit then closing connection."]);
objDatabaseInterface.connection.commit();
objDatabaseInterface.connection.rollback();    
objDatabaseInterface.close();
