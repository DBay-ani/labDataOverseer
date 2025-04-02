
--- CLEARLY this table could be refactored in a number of ways, particularly into better atoms,
--- but as mentioned in the commit message for f6501adb9e910da965c65eaa8e45ce74a955c996,
--- the calculas of the group at present makes one lean towards this design - which is 
--- more specific to the use case - then a ore general and cleaner one.

CREATE TABLE IF NOT EXISTS MessageTable (
    --- actually unneed for the time being - we send things to a list based on the type of message.... # intendedReceipiant INTEGER # FOREIGN KEY (intendedReceipiant) REFERENCES ContactorsTable(ID)
    sessionID INTEGER,
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    timeAdded REAL, 
    timeSent REAL , --- might not be applicable to all messages - specifically those received instead of sent....
    status TEXT NOT NULL,
    message BLOB NOT NULL,
    isGeneralMaintenceAndInfo INTEGER NOT NULL,
    isProblem INTEGER NOT NULL,
    IDOfSpecificOtherEndpointIfApplicable INTEGER,
    misc BLOB, --- "Safety valve" for other things; could also just be blob type..... 
    FOREIGN KEY( IDOfSpecificOtherEndpointIfApplicable ) REFERENCES ContactorsTable (ID), --- Note that since we did not add a NOT NULL
        --- constraint to IDOfSpecificOtherEndpointIfApplicable, it is allowed to be NULL despite this FOREIGN KEY contraint.
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID),
    CHECK(status in ('pending_send', 'error_sending', 'sent', 'received')),
    CHECK( isGeneralMaintenceAndInfo in (0,1)),
    CHECK( isProblem in (0,1)),
    CHECK( (timeAdded is NULL) or (timeAdded > 0)),
    CHECK( (timeSent is NULL) or ( (timeAdded is not NULL) and (timeSent >= timeAdded))) ----  not designed to send messages prior to adding to the OutgoingMessage table
);
--- Below needs to be a temp trigger since CurrentSession is a temporary table, whose 
--- value we use below. 
CREATE TEMP TRIGGER AddTimingInfo_Message
AFTER INSERT ON MessageTable
FOR EACH ROW 
BEGIN
    UPDATE MessageTable SET 
        timeAdded=unixepoch('subsec','utc') ,
        sessionID=(SELECT * FROM CurrentSession)
    WHERE ID=new.ID;
END;

