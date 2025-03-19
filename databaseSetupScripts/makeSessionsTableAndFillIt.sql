

--- For the below line, see https://stackoverflow.com/a/3020229 ; not sure if the Python interface preserves the
--- PRAGMA invocation across calls etc.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Sessions (
    ID INTEGER PRIMARY KEY, 
    timeStarted INTEGER DEFAULT CURRENT_TIMESTAMP );
---- By making CurrentSession a temporary table:
---- (1) it ensures that in memory each connection has a 
----     seperated version, as desired,
---- (2) it is ensured to have a fresh value corresponding
----     to the new connection each time, as desired.
CREATE TEMP TABLE CurrentSession (
    ID INTEGER, 
    FOREIGN KEY( ID ) REFERENCES Sessions(ID) );
CREATE TEMP TRIGGER storeCurrentSess 
AFTER INSERT ON Sessions 
FOR EACH ROW BEGIN 
    INSERT INTO CurrentSession (ID) VALUES (new.ID); 
END ;
INSERT INTO Sessions DEFAULT VALUES;

