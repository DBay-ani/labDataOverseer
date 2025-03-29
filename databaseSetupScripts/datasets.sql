CREATE TABLE IF NOT EXISTS Datasets (
    sessionID INTEGER,
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL, --- SQLite3 seems to restrict to one primary key... ---- PRIMARY KEY, 
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


CREATE TABLE IF NOT EXISTS DataContentType (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    sessionID INTEGER,
    name TEXT  UNIQUE NOT NULL, --- SQLite3 seems to restrict to one primary key... ---- PRIMARY KEY,
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
INSERT OR IGNORE INTO DataContentType ( name, misc) 
VALUES
    ( 'OFP', 'orange fluorescent protein'),
    ( 'BFP', 'blue fluorescent protein'),
    ( 'google_sheet', 'The Google sheet that the data collector/experimenter used to record the conditions collected.'),
    ( 'mNeptune', NULL),
    ( 'freely_moving', NULL), --- TODO
    ( 'NIR', 'Near Infrared recording of the E Elegans worm while freely moving.');

---- rowID, sessionID, datasetID, filePath , dateRecordADded , dataRecordType, misc (TEXT)
CREATE TABLE IF NOT EXISTS DatasetContent (
    sessionID INTEGER,
    rowID INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT  UNIQUE NOT NULL, --- SQLite3 seems to restrict to one primary key... ---- PRIMARY KEY, -- file path or URL....
    timeAdded INTEGER DEFAULT CURRENT_TIMESTAMP NOT NULL,
    datasetMemberOf INTEGER NOT NULL, 
    dataRecordType INTEGER NOT NULL, 
    misc TEXT, 
    FOREIGN KEY( datasetMemberOf ) REFERENCES Datasets(ID)
    FOREIGN KEY( dataRecordType ) REFERENCES DataContentType(ID)
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID)
    );
CREATE TEMP TRIGGER AddSessionInfo_DatasetContent
AFTER INSERT ON Datasets
FOR EACH ROW 
BEGIN
    UPDATE Datasets SET 
        sessionID=(SELECT * FROM CurrentSession)
    WHERE rowID=new.rowID;
END;

CREATE VIEW IF NOT EXISTS DatasetAndMostRecentIndividualFiles(
    datasetID,
    datasetName,
    dataContentTypeName,
    location
    )
AS SELECT 
    A1.ID,
    A1.name,
    B1.name,
    C1.location
FROM
    Datasets AS A1,
    DataContentType AS B1,
    DatasetContent as C1
WHERE
    C1.dataRecordType=B1.ID AND
    C1.datasetMemberOf = A1.ID
GROUP BY 
    A1.ID,
    B1.ID
HAVING
    C1.timeAdded = max(C1.timeAdded);


CREATE VIEW IF NOT EXISTS DatasetAndMostRecentFiles (
    datasetID,
    datasetName,
    OFP,
    BFP,
    google_sheet,
    mNeptune,
    freely_moving,
    NIR
    )
AS SELECT 
    A1.ID,
    A1.name,
    B1.location,
    B2.location,
    B3.location,
    B4.location,
    B5.location,
    B6.location
FROM
    Datasets AS A1,
    DatasetAndMostRecentIndividualFiles AS B1,
    DatasetAndMostRecentIndividualFiles AS B2,
    DatasetAndMostRecentIndividualFiles AS B3,
    DatasetAndMostRecentIndividualFiles AS B4,
    DatasetAndMostRecentIndividualFiles AS B5,
    DatasetAndMostRecentIndividualFiles AS B6
WHERE
    B1.datasetID=A1.ID AND
    B2.datasetID=A1.ID AND
    B3.datasetID=A1.ID AND
    B4.datasetID=A1.ID AND
    B5.datasetID=A1.ID AND
    B6.datasetID=A1.ID AND
    B1.dataContentTypeName='OFP' AND
    B2.dataContentTypeName='BFP' AND
    B3.dataContentTypeName='google_sheet' AND
    B4.dataContentTypeName='mNeptune' AND
    B5.dataContentTypeName='freely_moving' AND
    B6.dataContentTypeName='NIR';



