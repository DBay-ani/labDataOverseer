CREATE TABLE Datasets (
    sessionID INTEGER,
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT PRIMARY KEY, 
    timeStarted INTEGER DEFAULT CURRENT_TIMESTAMP NOT NULL,
    misc TEXT, 
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID)
    );
CREATE TEMP TRIGGER AddSessionInfo_Datasets
AFTER INSERT ON Datasets
FOR EACH ROW 
BEGIN
    UPDATE Datasets SET 
        sessionID=(SELECT * FROM CurrentSession)
    WHERE ID=new.ID;
END;


CREATE TABLE DataContentType (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    sessionID INTEGER,
    name TEXT PRIMARY KEY,
    misc TEXT,
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID)
    );
CREATE TEMP TRIGGER AddSessionInfo_DataContentType
AFTER INSERT ON DataContentType
FOR EACH ROW 
BEGIN
    UPDATE DataContentType SET 
        sessionID=(SELECT * FROM CurrentSession)
    WHERE ID=new.ID;
END;
INSERT INTO OR ABORT DataContentType ( name, misc) 
VALUES
    ( 'OFP', 'orange fluorescent protein'),
    ( 'BFP', 'blue fluorescent protein'),
    ( 'google_sheet', 'The Google sheet that the data collector/experimenter used to record the conditions collected.'),
    ( 'mNeptune', NULL),
    ( 'free_moving', NULL), --- TODO
    ( 'NIR', 'Near Infrared recording of the E Elegans worm while freely moving.');

---- rowID, sessionID, datasetID, filePath , dateRecordADded , dataRecordType, misc (TEXT)
CREATE TABLE DatasetContent (
    sessionID INTEGER,
    rowID INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT PRIMARY KEY, -- file path or URL....
    timeAdded INTEGER DEFAULT CURRENT_TIMESTAMP NOT NULL,
    datasetMemberOf INTEGER NOT NULL, 
    dataRecordType INTEGER NOT NULL, 
    misc TEXT, 
    FOREIGN KEY( datasetMemberOf ) REFERENCES Datasets(ID)
    FOREIGN KEY( dataRecordType ) REFERENCES DataContentType(ID)
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID)
    );
CREATE TEMP TRIGGER AddSessionInfo_Datasets
AFTER INSERT ON Datasets
FOR EACH ROW 
BEGIN
    UPDATE Datasets SET 
        sessionID=(SELECT * FROM CurrentSession)
    WHERE rowID=new.rowID;
END;

CREATE VIEW DatasetAndMostRecentIndividualFiles(
    datasetID,
    datasetName,
    dataContentTypeName,
    location
    )
SELECT 
    A1.ID,
    A1.name,
    B1.name,
    C1.location
FROM
    Datasets AS A1,
    DataContentType AS B1,
    DatasetContent as C1,
WHERE
    C1.dataRecordType=B1.ID AND
    C1.datasetMemberOf = A1.ID
GROUP BY 
    A1.datasetID,
    B1.ID
HAVING
    C1.timeAdded = max(C1.timeAdded);


CREATE VIEW DatasetAndMostRecentFiles (
    datasetID,
    datasetName,
    OFP,
    BFP,
    google_sheet,
    mNeptune,
    freely_moving,
    NIR
    )
SELECT 
    A1.ID,
    A1.name,
    B1.location,
    B2.location,
    B3.location,
    B4.location,
    B5.location,
    B6.location
WHERE
    B1.datasetMemberOf=A1.ID AND
    B2.datasetMemberOf=A1.ID AND
    B3.datasetMemberOf=A1.ID AND
    B4.datasetMemberOf=A1.ID AND
    B5.datasetMemberOf=A1.ID AND
    B6.datasetMemberOf=A1.ID AND
    B1.dataContentTypeName='OFP' AND
    B2.dataContentTypeName='BFP' AND
    B3.dataContentTypeName='google_sheet' AND
    B4.dataContentTypeName='mNeptune' AND
    B5.dataContentTypeName='freely_moving' AND
    B6.dataContentTypeName='NIR';



