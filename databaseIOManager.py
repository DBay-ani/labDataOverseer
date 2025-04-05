

import config;
_LOCALDEBUGFLAG = config.debugFlags.get_v_print_ForThisFile(__file__);
    

from utils.contracts import *;
import sqlite3
import config; 
import pickle;
import sys;

class DatabaseInterface():

    def open(self):
        raise NotImplementedError();
        return;

    # Executes the command and returns the result.
    # Returns all rows given by the result - to retrieve
    #     only a subset of the rows, the SQL command provided
    #     must use the LIMIT clause. Result will be returned as 
    #     list of dictionaries that each map a column name to a value...
    def exec(sqlCommandString):
        requires(isinstance(sqlCommandString, str));
        raise NotImplementedError();
        return;

    def commit(self):
        raise NotImplementedError();
        return;

    def rollback(self):
        raise NotImplementedError();
        return;

    def close(self):
        raise NotImplementedError();
        return;

    def executeScriptFile(self, scriptName):
        raise NotImplementedError();
        return;


class Sqlite3Database(DatabaseInterface):
    
    def __init__(self, databaseName=config.defaultValues.databaseName):
        self.databaseName = databaseName;
        self.executedCommandAfterLastCommit = False;
        self.connection= None;
        self.cursor = None;
        return

    def open(self):
        self.connection = sqlite3.connect(self.databaseName , \
                              autocommit=False,\
                              timeout=config.defaultValues.databaseWriteTimeoutLimit);

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d;
        self.connection.row_factory = dict_factory;

        self.cursor = self.connection.cursor();
        # For the below, see, for instance, https://stackoverflow.com/questions/29420910/how-do-i-enforce-foreign-keys/74947340#74947340
        self.connection.execute('PRAGMA foreign_keys = ON');
        ensures(self.connection is not None);
        ensures(self.cursor is not None);
        return;

    def exec(self, sqlCommandString):
        requires(isinstance(sqlCommandString, str));
        requires(self.connection is not None);

        # ssh-rsa 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 abc@defg

        self.executedCommandAfterLastCommit = True;
        self.cursor.execute(sqlCommandString); # Note that this method can only handle one SQL
            # command at a time. This could be worked-around to some degree by splitting commands
            # on the occurance of semicolons, but that in general is not a good approach when 
            # the content might hold strings.
        resultToReturn = self.cursor.fetchall();
        ensures(isinstance(resultToReturn, list));
        ensures(all([isinstance(x, dict) for x in resultToReturn]));
        return resultToReturn;


    def commit(self):
        requires(self.connection is not None);
        self.connection.commit();
        self.executedCommandAfterLastCommit = False;
        return;

    def close(self):
        requires(self.connection is not None);
        if( self.executedCommandAfterLastCommit):
            sys.stderr.write("Warning: There have been commands executed since the last database commit." + \
                  "\n    Currently closing the database now, so any changes made since the last commit " + \
                  "\n    will be lost.\n\n");
            sys.stderr.flush();
        self.connection.close();
        return;

    def rollback(self):
        requires(self.connection is not None);
        raise NotImplementedError();
        return;

    def executeScriptFile(self, scriptName): # This function does not return anything...
        requires(isinstance(scriptName, str));
        requires(" " not in scriptName);
        fh = open(scriptName, 'r');
        sqlScript = fh.read();
        fh.close();
        self.cursor.executescript(sqlScript);
        return;

    def interfaceBleed_insertValuesForBlob(self, primarySQLCommand, blobValuesToRecord):
        requires(isinstance(primarySQLCommand, str));
        requires(len(primarySQLCommand) > 0);
        requires(isinstance( blobValuesToRecord, list));
        requires(len(blobValuesToRecord) == primarySQLCommand.count("?"));
        listOfObjectsConvertedToBinary = \
            [sqlite3.Binary(pickle.dumps(x)) for x in blobValuesToRecord];
        self.cursor.execute(primarySQLCommand, listOfObjectsConvertedToBinary);
        return;



def recordRunContext():
    objDatabaseInterface.connection.rollback();
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Gathering process context information at start of run."]); 
    objDatabaseInterface.connection.commit();


    dictToWrite=dict();
    for command in [ ['id'], ['hostname'], ['cat', '/etc/machine-id'], ['pwd'], ['git', 'status'], ['git', 'log', '-n1'], ['env'], ['git', 'diff', 'HEAD']]:
        try:
            stdout=runSystemCall(command);
        except:
            fileName=__file__.split("/")[-1];
            handleError("Handling the following error then continuing. Note: the error was generated when "+\
                f"making the system call `{command}`  in the `recordRunContext` function in file {fileName}. Error information:\n");


        contextKey=repr(command);
        contextValue=str(stdout); # NOTE: we could consider enforcing length limits here, but for this particular function (which should
                                  #     only be run once for the process and overseen by the admin starting the scripts etc.),
                                  #     it is likely unnecessary. For system calls and reading user-provided files more
                                  #     generally, though, that may be prudent.

        objDatabaseInterface.cursor.execute("INSERT INTO SessionContextWhenStarted (contextKey, contextValue) VALUES (?, ?)", [contextKey, contextValue]); 
        objDatabaseInterface.connection.commit();

    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", ["Done gathering process context information at start of run."]); 
    objDatabaseInterface.connection.commit();
        
    return;


from typing import Tuple, Any, List ;

def attemptSetDefaultValues(objDatabaseInterface):
    commandsAndVars : List[Tuple[str, Tuple[Any,...]]]= [\
        ("INSERT OR IGNORE INTO ContactorsTable (" +\
            "name, contactInfo, notifyAboutGeneralMaintenceAndInfo, notifyWhenAdditions, notifyWhenProblem, endpointType) "+ \
            "VALUES (?, ?, ?, ?, ?, ?)", ('DefaultMessageReceptionPoint', config.defaultValues.directory_communication_incoming, 0, 0, 0, 'file_directory') ), \
        ("INSERT OR IGNORE INTO ContactorsTable (" +\
            "name, contactInfo, notifyAboutGeneralMaintenceAndInfo, notifyWhenAdditions, notifyWhenProblem, endpointType) "+ \
            "VALUES (?, ?, ?, ?, ?, ?)", ('DefaultLocationToSendMessagesReceivedAtDefaultMessageReceptionPoint', config.defaultValues.directory_communication_outgoing, 0, 0, 0, 'file_directory') ) \
    ]; 
    for thisCommand, theseVars in commandsAndVars:
        objDatabaseInterface.cursor.execute(thisCommand, theseVars);
    
    return;


objDatabaseInterface = Sqlite3Database();
# NOTE: since the two packages imported below ALSO IMPORT THIS FILE (well,objDatabaseInterface specifically)
# from it), they need to do below to avoid circular imports.
from utils.runSystemCall import runSystemCall;
from utils.handleError import handleError;


objDatabaseInterface.open();
# Note that the script generating the session table and current session value
# needs to go before anything else
for thisScriptFile in [
        "makeSessionsTableAndFillIt.sql",\
        "makeContextTable.sql", \
        "makeContactorsTable.sql",\
        "makeMessageTable.sql",\
        "makeRunLogsTable.sql", \
        "datasets.sql", \
        "blobStore.sql" \
    ]:
    objDatabaseInterface.executeScriptFile(\
        "databaseSetupScripts/" + thisScriptFile);
    objDatabaseInterface.commit();
    
recordRunContext();
attemptSetDefaultValues(objDatabaseInterface);
objDatabaseInterface.commit();



def executeDatabaseCommandList(commandsToExecute):
    for thisCommand in commandsToExecute:
        objDatabaseInterface.exec(thisCommand);
    objDatabaseInterface.commit();
    return;


