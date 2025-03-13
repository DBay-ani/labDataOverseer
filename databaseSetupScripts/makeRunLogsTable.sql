CREATE TABLE RunLogsTable (
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    unixEpochTime  REAL, 
    humanReadableTime TEXT, 
    logInfo TEXT,
    _blob_log_in_case BLOB,
    CHECK( (unixEpochTime is NULL) or (unixEpochTime > 0)),
    CHECK( (humanReadableTime is NULL) or (length(humanReadableTime) > 0) ),
    CHECK( (unixEpochTime is NULL)  == (humanReadableTime is NULL) )
);
CREATE TRIGGER AddTimingInfo_RunLogsTable 
AFTER INSERT ON RunLogsTable
FOR EACH ROW 
BEGIN
    UPDATE RunLogsTable SET 
        unixEpochTime=unixepoch('subsec','utc') , 
        humanReadableTime=strftime('s%fm%Mhtw%Hd%dM%my%YtzUTC', 'now', 'utc', 'subsec')
    WHERE ID=new.ID;
END;
