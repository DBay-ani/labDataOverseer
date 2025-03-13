CREATE TABLE OutgoingMessageTable (
    --- actually unneed for the time being - we send things to a list based on the type of message.... # intendedReceipiant INTEGER # FOREIGN KEY (intendedReceipiant) REFERENCES ContactorsTable(ID)
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    timeAdded REAL, 
    timeSent REAL ,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    isGeneralMaintenceAndInfo INTEGER NOT NULL,
    isDataAddition INTEGER NOT NULL,
    isProblem INTEGER NOT NULL,
CHECK(status in ('pending', 'error', 'sent')),
CHECK( isGeneralMaintenceAndInfo in (0,1)),
CHECK( isDataAddition in (0,1) ),
CHECK( isProblem in (0,1)),
CHECK( (timeAdded is NULL) or (timeAdded > 0)),
CHECK( (timeSent is NULL) or ( (timeAdded is not NULL) and (timeSent >= timeAdded))) ----  not designed to send messages prior to adding to the OutgoingMessage table
);
CREATE TRIGGER AddTimingInfo_OutgoingMessage
AFTER INSERT ON OutgoingMessageTable
FOR EACH ROW 
BEGIN
    UPDATE OutgoingMessageTable SET 
        timeAdded=unixepoch('subsec','utc') 
    WHERE ID=new.ID;
END;
