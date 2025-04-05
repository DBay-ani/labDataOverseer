import sqlite3
import config;
from utils.contracts import requires, ensures;

import subprocess;

import sys ;

from databaseIOManager import objDatabaseInterface; 

import time;
import typing;

import os ;
import traceback; 

from utils.handleError import handleError;

import json;
import datetime;

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

from interface_dfe6f45f_265d_470d_bcdb_66d1e6dcdc39 import interface_dfe6__dc39__sweet_orchestra;

# Starting with a double underscore in the below variable name so that the content can't be accidentally
# imported elsewhere
__listOfAvailableInterfaces=[interface_dfe6__dc39__sweet_orchestra];

# TODO: consider just having a flie called LAST_CHECKED that is updated any time the 
#     process checks the folder, and leave the files where they are, only removing those
#     that are older than a certain amount.... this is instead of, say, moving the files to 
#     an intermediate directory then doing that stuff....


def issueReply(originalFileName : str, errorDetected: bool,  contentOfReply : dict, 
     timeReceivedAsReadableString: str) -> None:

    placeToSaveReply=config.defaultValues.directory_communication_outgoing + \
        "REPLY_FOR_" + originalFileName + "_SENT_"+str(time.ctime().replace(" ","_").replace(":", "-")) + ".json";

    # TODO (in future iterations): record in the message table as pending and
    # update it to sent further below....


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


    # The below line/two lines forming IDForEndpointSentTo are a mess.... also, 
    # the TODO(8691d5f6-3a7f-4dac-acea-d4b71b32e99f) below might be usefule, since the information provided
    # on the below line should come in earlier etc.
    IDForEndpointSentTo= [x for x in objDatabaseInterface.cursor.execute(\
        "SELECT ID FROM ContactorsTable WHERE name=?", ["DefaultLocationToSendMessagesReceivedAtDefaultMessageReceptionPoint"])][0]["ID"];
    objDatabaseInterface.cursor.execute("""
        INSERT INTO MessageTable ( status, message, isGeneralMaintenceAndInfo, 
            isProblem, IDOfSpecificOtherEndpointIfApplicable )  
        VALUES (?, ?, ?, ?, ?)""", \
        ["sent", fileContent, 0, ( 1 if errorDetected else 0), IDForEndpointSentTo ]);
    objDatabaseInterface.connection.commit();

    return;


def formReplyStatingErrorOccurred(fullPath : str, fileName:str, errorMessageIndented:str, timeReceivedAsReadableString:str) -> None:
    objDatabaseInterface.connection.rollback();
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
        [f"Issuing reply to received message \"{fullPath}\" indicating error occurred."]);
    objDatabaseInterface.connection.commit();

    issueReply(fileName, errorDetected=True,  contentOfReply={"ERROR_MESSAGE":errorMessageIndented}, \
        timeReceivedAsReadableString=timeReceivedAsReadableString);
 
    return; 

from utils.runSystemCall import runSystemCall;


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
        
        # TODO(8691d5f6-3a7f-4dac-acea-d4b71b32e99f): rewrite this to read from the database the location and endpoint type of 
        #     DefaultMessageReceptionPoint and, based on that information, read from the correct place
        #     and do so in the correct fashion.

        # Note: attempting to read or accese metadata about the file might run into permission errors, but
        # then that would be caught and reported by the try-except block we're in.
        if(not os.path.isfile(fullPath) ):
            errorMessageIndented=handleError(\
                f"    Will not / cannot process received message \"{fullPath}\" beyond moving it under directory \"{config.defaultValues.placeToMoveOldInboxContentTo}\": content is not a file (e.g., is a directory, link, or so forth).");
            ### would be nice to handle this with actual control flow that is not a hammer, but that prettiness / cleanliness can wait a bit at minimal cost..... #### formReplyStatingErrorOccurred(fullPath,fileName, errorMessageIndented, timeReceivedAsReadableString);
            raise Exception(errorMessageIndented);           
        assert(os.path.isfile(fullPath));
        if( os.path.getsize(fullPath) > config.defaultValues.maxSizeCommunicationWillReadInBytes):
            errorMessageIndented=handleError(\
            f"    Will not process received message \"{fullPath}\": the content is larger than the maximum file size we consider processing, {config.defaultValues.maxSizeCommunicationWillReadInBytes} bytes.");
            ### We considered adding the log to move the file, but doing that in a way that also ensure recordinf of errors and robustness is effort not best spent right now.....# f"    Will not process received message \"{fullPath}\"  beyond moving it under directory \"{configs.defaultValues.placeToMoveOldInboxContentTo}\": the content is larger than the maximum file size we consider processing, {configs.defaultValues.maxSizeCommunicationWillReadInBytes} bytes.");
            raise Exception(errorMessageIndented);


        fh=open(fullPath, "rb");
        fhContent=fh.read(config.defaultValues.maxSizeCommunicationWillReadInBytes);
        if(len(fh.read()) > 0):
            fh.close();
            raise Exception(f"Content in file \"{fullPath}\" which was provided as a request to the system, is larger"+\
                            f" than the maximum size we're willing to process of {config.defaultValues.maxSizeCommunicationWillReadInBytes}.");
        fh.close();

        objDatabaseInterface.connection.rollback();
        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
            [f"Read \"{fullPath}\" into memory; length of content: {len(fullPath)}."]);
        objDatabaseInterface.connection.commit();
        
        # The below line/two lines forming IDForEndpointReadFrom are a mess.... also, 
        # see TODO(8691d5f6-3a7f-4dac-acea-d4b71b32e99f) above, since the information provided
        # on the below line should come in earlier etc.
        IDForEndpointReadFrom= [x for x in objDatabaseInterface.cursor.execute(\
            "SELECT ID FROM ContactorsTable WHERE name=?", ["DefaultMessageReceptionPoint"])][0]["ID"];
        extraInfo="";
        try:
            # NOTE: the use of "stat" below allows us to record more metadata- IN PARTICULAR WHO MADE THE REQUEST.
            # TODO: in future iterations of the database, record this additional messsage data in a more principle way.....
            extraInfo=runSystemCall(["stat", fullPath]);
        except Exception as e:
            # NOTE: the logging already present in runSystemCall should record in the database that an error 
            # occurred etc., so if we don't right that to the run-log here, it not the end of the world since
            # we already have a record of that information.
            extraInfo=f"Error occurred running 'stat {fullPath}'. Details:\n" +str(e);
        objDatabaseInterface.cursor.execute("""
            INSERT INTO MessageTable ( status, message, isGeneralMaintenceAndInfo, 
                isProblem, IDOfSpecificOtherEndpointIfApplicable, misc )  
            VALUES (?, ?, ?, ?, ?, ?)""", \
            ["received", fhContent, 0, 0, IDForEndpointReadFrom, extraInfo ]);
        objDatabaseInterface.connection.commit();

        objDatabaseInterface.connection.rollback();
        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
            [f"Saved message \"{fullPath}\" into database table \"MessageTable\"."]);
        objDatabaseInterface.connection.commit();

        # Note that the below can - and should - be able to replace in the target location and file that
        # happens to have the same name.
        # This moving is meant as a convieniance and indicator to the user, not any deeper form of 
        # content backup.
        newLocationForFile=config.defaultValues.placeToMoveOldInboxContentTo + \
            "RECEIVED_AT_"+str(time.ctime().replace(" ","_").replace(":", "-")) +"__"+ fileName;
        
        os.replace(fullPath, newLocationForFile);
        objDatabaseInterface.connection.rollback();
        objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
            [f"Moved \"{fullPath}\" to {newLocationForFile}."]);
        objDatabaseInterface.connection.commit();


        # NOTE: we put a seperate try-except block below so that we can  provided 
        #     the user more feedback on the cause of this issue, since we suspect this
        #     might be a relatively common cause of problem (at least proportionally among the
        #     hopefully slim number of issues people have).
        readJSONContent:typing.Optional[typing.Dict[str,typing.Any]]=None;
        try:
           # TODO: attempt reading the JSON file
           readJSONContent=json.loads(fhContent);
        except Exception as e:
            errorMessage=f"Exception occurred while trying to read / parse the file \"{fullPath}\". Note: often, but not always, this is because the file you"+\
                " provided has some small syntax mistake that causes it to be invalid JSON - see the rest of this error message to get a further hint as to the cause:\n";   
            raise Exception(errorMessage);

        assert(isinstance(readJSONContent,dict));
        # NOTE: we don't just add in "interface_id" if it is missing because what if someone tried to add it and 
        # misspelled it or something similar. Proceeding might cause more confusion then help.
        if(set(readJSONContent.keys()).issubset({"request", "content"})):
            readJSONContent["interface_id"]=config.defaultValues.defaultInterfaceForFileCommunication;

        if("interface_id" not in readJSONContent):
            raise Exception("The JSON file provided does not specify a value for key \"interface_id\" " + \
                            "(without this, we don't know how the rest of the file should be interpretted).");
        if(not isinstance(readJSONContent["interface_id"], str)):
            raise Exception("The interface_id provided is not text, but instead is of type "+\
                             str(type(readJSONContent["interface_id"])));


        # TODO(19e8f005-450a-4790-9ee9-0eead5001b4c): make case-insensative key-match (which of course also involves signalling error
        #     if there is a key-clash).
        matchingInterface=[thisInterface for thisInterface in __listOfAvailableInterfaces \
                           if (thisInterface.get_human_readable_name() == readJSONContent["interface_id"])];
        if(len(matchingInterface) == 0):
            raise Exception("The interface_id specified does not match any interface available.");
        elif(len(matchingInterface) > 1):
            raise Exception("The iterface_id provided matches more than one interface available. "+\
                            f"Number matching: {matchingInterface}. Speak to a server admin about this.");
        assert(len(matchingInterface) == 1);
        # On the below line, the () are to instantiate an instance of the class, since above
        # we only dealt with the static methods of the class.
        contentReceivedBack=matchingInterface[0]().process(readJSONContent);
        issueReply(fileName, \
            errorDetected=False, \
            contentOfReply=contentReceivedBack, \
            timeReceivedAsReadableString=timeReceivedAsReadableString);
        
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
    for thisF in os.listdir(config.defaultValues.directory_communication_incoming):
        assert(os.path.exists(config.defaultValues.directory_communication_incoming + thisF));
        handleMessage(config.defaultValues.directory_communication_incoming+thisF, thisF);   
    return ;




# TODO: add a routine to clean old message out (say, if older than 20 minutes or so.....) That would 
#     be better to eventually place in the daemon that checks files paths are present and sends out emails
#     if they are not
routinesToCallAndTheirName=[ \
    (readAndAddressMessages,"ReadAndAddressMessages")
];


try:

    cycleNumber=0;
    while(True):

        print(f"{cycleNumber}",flush=True);

        if(cycleNumber % config.defaultValues.communicationDaemon_logCycleFrequency == 0):
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
            if(cycleNumber % config.defaultValues.communicationDaemon_logCycleFrequency == 0):
                # Not logging every cycle since this is expected to run far more often
                # than the other Daemon
                objDatabaseInterface.connection.rollback();
                objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
                    [f"Starting execution of subroutine \"{subRoutineName}\"."]);
                objDatabaseInterface.connection.commit();

            try:
                thisSubRoutine(); #objDatabaseInterface);
            except:
                handleError(f"An exception has occurred while running subroutine {subRoutineName}");

        if(cycleNumber % config.defaultValues.communicationDaemon_logCycleFrequency == 0):
            # Not logging every cycle since this is expected to run far more often
            # than the other Daemon

            objDatabaseInterface.connection.rollback();
            objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
                [f"Ending Loop Cycle Number {cycleNumber} of this execution of `{thisFileName}`. "+\
                 f"Proceeding to sleep for {config.defaultValues.timeToSleepBetweenChecks} seconds after committing this."]);
            objDatabaseInterface.connection.commit();

        cycleNumber=cycleNumber+1;

        objDatabaseInterface.connection.commit();

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
