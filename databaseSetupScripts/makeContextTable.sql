
CREATE TABLE IF NOT EXISTS SessionContextWhenStarted (
    sessionID INTERGER,
    contextKey TEXT NOT NULL,
    contextValue TEXT, --- we do not require context values to be non-null
    UNIQUE(sessionID, contextKey),
    FOREIGN KEY ( sessionID) REFERENCES Sessions (ID),
    CHECK(length(contextKey) > 0) --- we do not require the context values to be non-empty strings
);
---  Below needs to be a temporary trigger since the table being read is temporary--- a 
--- design that helps mutliple process accessing the database store ther own version and
--- ensures it is up-to-date with the currently running process
CREATE TEMP TRIGGER InsertSessionIDInto_SessionContextWhenStarted
AFTER INSERT ON SessionContextWhenStarted
FOR EACH ROW
BEGIN
    UPDATE SessionContextWhenStarted
    SET
        sessionID=(SELECT * FROM CurrentSession)
    WHERE
        --- You should be able to get away with only one of
        --- the two conditions below and produce and equivalent
        --- effect, but I'm not in general a fan of using rowID
        --- (preferring explicit primary keys, but those are
        --- not present here --- due to the desire for explicit
        --- nullability in the sessionID so this trigger can 
        --- fill it) and going with the NULL-check alone feels
        --- less robust than I would like.
        rowID=new.rowID AND
        (sessionID is NULL);
END;

