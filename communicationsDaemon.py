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

# TODO: consider just having a flie called LAST_CHECKED that is updated any time the 
#     process checks the folder, and leave the files where they are, only removing those
#     that are older than a certain amount.... this is instead of, say, moving the files to 
#     an intermediate directory then doing that stuff....


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

        if(not os.path.isfile(x) ):
            errorMessageIndented=handleError(\
                f"    Will not / cannot process received message \"{fullPath}\" beyond moving it under directory \"{configs.defaultValues.placeToMoveOldInboxContentTo}\": content is not a file (e.g., is a directory, link, or so forth).");
            ### would be nice to handle this with actual control flow that is not a hammer, but that prettiness / cleanliness can wait a bit at minimal cost..... #### formReplyStatingErrorOccurred(fullPath,fileName, errorMessageIndented, timeReceivedAsReadableString);
            raise Exception(errorMessageIndented);           
        if( os.path.getsize(fullPath) > configs.defaultValues.maxSizeCommunicationWillReadInBytes):
            errorMessageIndented=handleError(\
            f"    Will not process received message \"{fullPath}\"  beyond moving it under directory \"{configs.defaultValues.placeToMoveOldInboxContentTo}\": the content is larger than the maximum file size we consider processing, {configs.defaultValues.maxSizeCommunicationWillReadInBytes} bytes.");
            raise Exception(errorMessageIndented);

        # Note: attempting to read the file might run into permission errors, but
        # then that would be caught and reported by the try-except block we're in.
        # TODO: open file for reading        
        # TODO: save message into table
        # TODO: attempt to move message 

        # NOTE: we put a seperate try-except block below so that we can  provided 
        #     the user more feedback on the cause of this issue, since we suspect this
        #     might be a relatively common cause of problem (at least proportionally among the
        #     hopefully slim number of issues people have).
        try:
           # TODO: attempt reading the JSON file
        except Exception as e:
            errorMessage=f"Exception occurred while trying to read / parse the file \"{fullPath}\". Note: often, but not always, this is because the file you"+\
                " provided has some small syntax mistake that causes it to be invalid JSON - see the rest of this error message to get a further hint as to the cause:\n";   
            raise Exception(errorMessage);

        # TODO: pass the json to the correct function to handle the request.

         
        assert(os.path.isfile(x));
    except:
        errorMessageIndented=handleError(f"Error while processing received message \"{fullPath}\".");
        formReplyStatingErrorOccurred(fullPath,fileName, errorMessageIndented, timeReceivedAsReadableString);         

    objDatabaseInterface.connection.rollback();
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
        [f"End of processing of received message \"{fullPath}\"."]);
    objDatabaseInterface.connection.commit();
    return;

"""
baseOfCommunicationsLocations="/home/b4ba59dcd2b847bb9b12155facf1f0ce/";
directory_communication_incoming=baseOfCommunicationsLocations+"tempDataStore/inbox/";
placeToMoveOldInboxContentTo=baseOfCommunicationsLocations+"tmp/external/";
directory_communication_outgoing=baseOfCommunicationsLocations+"tempDataStore/outbox/";


communicationDaemon_logCycleFrequency=1000;
timeToSleepBetweenChecks_communicationDaemon=5; # In seconds
timeToWaitBeforeDeletingOldReceivedMessageFiles=(24 * 3600); # In seconds
"""

def readAndAddressMessages() -> None:
    """Note the following:
    >>> os.listdir.__doc__
    "Return a list containing the names of the files in the directory.\n\npath can be specified as either str, bytes, or a path-like object.  If path is bytes,\n  the filenames returned will also be bytes; in all other circumstances\n  the filenames returned will be str.\nIf path is None, uses the path='.'.\nOn some platforms, path may also be specified as an open file descriptor;\\\n  the file descriptor must refer to a directory.\n  If this functionality is unavailable, using it raises NotImplementedError.\n\nThe list is in arbitrary order.  It does not include the special\nentries '.' and '..' even if they are present in the directory."
    """
    for thisF in os.listdir(configs.defaultValues.directory_communication_incoming):
        assert(os.path.exists(thisF));
        handleMessage(configs.defaultValues.directory_communication_incoming+thisF);   
    return ;





routinesToCallAndTheirName=[ \
    (readAndAddressMessage,"ReadAndAddressMessages")
];


try:

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
