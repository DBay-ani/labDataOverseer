
CREATE TABLE IF NOT EXISTS RunLogsTable (
    sessionID INTEGER,
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    unixEpochTime  REAL, 
    humanReadableTime TEXT, 
    logInfo TEXT,
    _blob_log_in_case BLOB,
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID),
    CHECK( (unixEpochTime is NULL) or (unixEpochTime > 0)),
    CHECK( (humanReadableTime is NULL) or (length(humanReadableTime) > 0) ),
    CHECK( (unixEpochTime is NULL)  == (humanReadableTime is NULL) )
);
--- Below needs to be a temp trigger since CurrentSession is a temporary table, whose 
--- value we use below. 
CREATE TEMP TRIGGER AddTimingInfo_RunLogsTable 
AFTER INSERT ON RunLogsTable
FOR EACH ROW 
BEGIN
    UPDATE RunLogsTable SET 
        unixEpochTime=unixepoch('subsec','utc') , 
        humanReadableTime=strftime('s%fm%Mhtw%Hd%dM%my%YtzUTC', 'now', 'utc', 'subsec'),
        sessionID=(SELECT * FROM CurrentSession)
    WHERE ID=new.ID;
END;

