CREATE TABLE IF NOT EXISTS OutgoingMessageTable (
    --- actually unneed for the time being - we send things to a list based on the type of message.... # intendedReceipiant INTEGER # FOREIGN KEY (intendedReceipiant) REFERENCES ContactorsTable(ID)
    sessionID INTEGER,
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    timeAdded REAL, 
    timeSent REAL ,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    isGeneralMaintenceAndInfo INTEGER NOT NULL,
    isDataAddition INTEGER NOT NULL,
    isProblem INTEGER NOT NULL,
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID),
    CHECK(status in ('pending', 'error', 'sent')),
    CHECK( isGeneralMaintenceAndInfo in (0,1)),
    CHECK( isDataAddition in (0,1) ),
    CHECK( isProblem in (0,1)),
    CHECK( (timeAdded is NULL) or (timeAdded > 0)),
    CHECK( (timeSent is NULL) or ( (timeAdded is not NULL) and (timeSent >= timeAdded))) ----  not designed to send messages prior to adding to the OutgoingMessage table
);
--- Below needs to be a temp trigger since CurrentSession is a temporary table, whose 
--- value we use below. 
CREATE TEMP TRIGGER AddTimingInfo_OutgoingMessage
AFTER INSERT ON OutgoingMessageTable
FOR EACH ROW 
BEGIN
    UPDATE OutgoingMessageTable SET 
        timeAdded=unixepoch('subsec','utc') ,
        sessionID=(SELECT * FROM CurrentSession)
    WHERE ID=new.ID;
END;
