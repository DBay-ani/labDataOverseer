CREATE TABLE IF NOT EXISTS SessionContextWhenStarted (
    sessionID INTERGER,
    contextKey TEXT NOT NULL,
    contextValue TEXT, --- we do not require context values to be non-null
    UNIQUE(sessionID, contextKey),
    FOREIGN KEY sessionID REFERENCES Sessions (ID),
    CHECK(length(contextKey) > 0) --- we do not require the context values to be non-empty strings
)
---  Below needs to be a temporary trigger since the table being read is temporary--- a 
--- design that helps mutliple process accessing the database store ther own version and
--- ensures it is up-to-date with the currently running process
CREATE TRIGGER InsertSessionIDInto_SessionContextWhenStarted
AFTER INSERT ON SessionContextWhenStarted
FOR EACH ROW
BEGIN
    UPDATE SessionContextWhenStarted
    SET
        new.sessionID=(SELECT * FROM CurrentSession);
END;

